# -*- coding: utf-8 -*-

from typing import Any, Iterable
from web3.types import EventData
from geodefi.globals import VALIDATOR_STATE
from geodefi.classes import Validator

from src.logger import log
from src.globals import SDK, chain
from src.classes import Trigger, Database
from src.daemons import TimeDaemon
from src.exceptions import BeaconStateMismatchError, DatabaseError, EthdoError
from src.utils import send_email
from src.actions import exit_validator
from src.helpers import (
    create_exit_request_table,
    event_handler,
    save_portal_state,
    save_local_state,
    save_exit_epoch,
    run_finalize_exit_triggers,
    check_pk_in_db,
)

from ..time.finalize_exit_trigger import FinalizeExitTrigger


class ExitRequestTrigger(Trigger):
    """Trigger for the EXIT_REQUEST event. This event is emitted when a validator requests to exit.

    Attributes:
        name (str): The name of the trigger to be used when logging (value: EXIT_REQUEST_TRIGGER)
    """

    name: str = "EXIT_REQUEST_TRIGGER"

    def __init__(self) -> None:
        """Initializes an ExitRequestTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.update_validators_status)
        # Runs finalize exit triggers if there are any validators to be finalized
        run_finalize_exit_triggers()
        create_exit_request_table()
        log.debug(f"{self.name} is initated.")

    def __filter_events(self, event: EventData) -> bool:
        """Filters the events to check if the event is in the validators table.

        Args:
            event (EventData): Event to be checked

        Returns:
            bool: True if the event is in the validators table, False otherwise
        """

        # if pk is in db (validators table), then continue
        return check_pk_in_db(event.args.pubkey)

    def __parse_events(self, events: Iterable[EventData]) -> list[tuple]:
        """Parses the events to saveable format. Returns a list of tuples. Each tuple represents a saveable event.

        Args:
            events (Iterable[EventData]): list of ExitRequest emits

        Returns:
            list[tuple]: list of saveable events
        """
        saveable_events: list[tuple] = []
        for event in events:
            saveable_events.append(
                (
                    event.args.pubkey,
                    event.blockNumber,
                    event.transactionIndex,
                    event.logIndex,
                )
            )

        return saveable_events

    def __save_events(self, events: list[tuple]) -> None:
        """Saves the events to the database.

        Args:
            events (list[tuple]): list of saveable events
        """
        try:
            with Database() as db:
                db.executemany(
                    "INSERT INTO ExitRequest VALUES (?,?,?,?,?,?,?)",
                    events,
                )
            log.debug(f"Inserted {len(events)} events into ExitRequest table")
        except Exception as e:
            raise DatabaseError(f"Error inserting events to table ExitRequest") from e

    def update_validators_status(self, events: Iterable[EventData], *args, **kwargs) -> None:
        """Updates the status of validators that have requested to exit the network.

        Args:
            events (Iterable[EventData]): The events to be processed and saved to the database.
        """
        log.info(f"{self.name} is triggered.")

        # filter, parse and save events
        filtered_events: Iterable[EventData] = event_handler(
            events,
            self.__parse_events,
            self.__save_events,
            self.__filter_events,
        )

        exitted_pks: list[str] = []
        for event in filtered_events:
            pubkey: str = event.args.pubkey
            save_portal_state(pubkey, VALIDATOR_STATE.EXIT_REQUESTED)

            # TODO: if this is not waiting for tx to be mined, there should be a way to handle and check the beacon_status
            try:
                exit_validator(pubkey)
            except EthdoError as e:
                send_email(e.__class__.__name__, str(e), [("<file_path>", "<file_name>.log")])
                continue

            val: Validator = SDK.portal.validator(pubkey)
            if val.beacon_status == "active_exiting":
                # write database the expected exit block
                # TODO: validator.withdrawable_epoch instead of exit_epoch
                save_exit_epoch(pubkey, val.exit_epoch)
                exitted_pks.append(pubkey)
            else:
                raise BeaconStateMismatchError(f"Beacon state mismatch for pubkey {pubkey}")

        # TODO: if exit_validator function (ethdo) is waiting for finalization, we do not need to
        #       seperate the for loops and we can continue under the same loop
        for pubkey in exitted_pks:
            save_local_state(pubkey, VALIDATOR_STATE.EXIT_REQUESTED)

            finalize_exit_trigger: FinalizeExitTrigger = FinalizeExitTrigger(pubkey)

            # calculate the delay for the daemon to run
            res: dict[str, Any] = SDK.beacon.beacon_headers_id("head")
            # pylint: disable=E1126:invalid-sequence-index
            slots_per_epoch: int = chain.slots_per_epoch
            slot_interval: int = int(chain.interval)

            current_slot: int = int(res["header"]["message"]["slot"])
            current_epoch: int = current_slot // slots_per_epoch

            if current_epoch >= val.exit_epoch:
                init_delay: int = 0
            else:
                epoch_diff: int = val.exit_epoch - current_epoch
                seconds_per_epoch: int = slots_per_epoch * slot_interval
                init_delay: int = epoch_diff * seconds_per_epoch

            # initialize and run the daemon
            finalize_exit_daemon: TimeDaemon = TimeDaemon(
                interval=slot_interval + 1,
                trigger=finalize_exit_trigger,
                initial_delay=init_delay,
            )

            finalize_exit_daemon.run()
