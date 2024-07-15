# -*- coding: utf-8 -*-

from typing import Any, Iterable
from web3.types import EventData
from geodefi.globals import VALIDATOR_STATE
from geodefi.classes import Validator

from src.classes import Trigger, Database
from src.daemons import TimeDaemon
from src.triggers.time import FinalizeExitTrigger
from src.exceptions import BeaconStateMismatchError, DatabaseError, EthdoError
from src.actions.ethdo import exit_validator
from src.database.validators import (
    save_portal_state,
    save_local_state,
    save_exit_epoch,
    check_pk_in_db,
)
from src.database.events import create_exit_request_table

from src.helpers.event import event_handler
from src.helpers.validator import run_finalize_exit_triggers
from src.globals import get_constants, get_sdk, get_logger
from src.utils.notify import send_email


class ExitRequestTrigger(Trigger):
    """Trigger for the EXIT_REQUEST event. This event is emitted when a validator requests to exit.

    Attributes:
        name (str): The name of the trigger to be used when logging (value: EXIT_REQUEST)
    """

    name: str = "EXIT_REQUEST"

    def __init__(self) -> None:
        """Initializes an ExitRequestTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.update_validators_status)
        # Runs finalize exit triggers if there are any validators to be finalized
        run_finalize_exit_triggers()
        create_exit_request_table()
        get_logger().debug(f"{self.name} is initated.")

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
                    event.args.pubkey,  # TEXT
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
                    "INSERT INTO ExitRequest VALUES (?,?,?,?)",
                    events,
                )
            get_logger().debug(f"Inserted {len(events)} events into ExitRequest table")
        except Exception as e:
            raise DatabaseError(f"Error inserting events to table ExitRequest") from e

    def update_validators_status(self, events: Iterable[EventData], *args, **kwargs) -> None:
        """Updates the status of validators that have requested to exit the network.

        Args:
            events (Iterable[EventData]): The events to be processed and saved to the database.
        """

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

            # TODO: (later) if this is not waiting for tx to be mined, there should be a way to handle and check the portal_state/beacon_status.
            try:
                exit_validator(pubkey)
            except EthdoError as e:
                send_email(e.__class__.__name__, str(e), dont_notify_devs=True)
                continue

            val: Validator = get_sdk().portal.validator(pubkey)
            if val.beacon_status == "active_exiting":
                # write database the expected exit block
                # TODO: (later) use validator.withdrawable_epoch instead of exit_epoch - today
                # also check for default withdrawable_epoch which is too_far_epoch
                save_exit_epoch(pubkey, val.exit_epoch)
                exitted_pks.append(pubkey)
            else:
                raise BeaconStateMismatchError(f"Beacon state mismatch for pubkey {pubkey}")

        # TODO: (later) if exit_validator function (ethdo) is waiting for finalization, we do not need to
        #       seperate the for loops and we can continue under the same loop
        for pubkey in exitted_pks:
            save_local_state(pubkey, VALIDATOR_STATE.EXIT_REQUESTED)

            # calculate the delay for the daemon to run
            res: dict[str, Any] = get_sdk().beacon.beacon_headers_id("head")
            # pylint: disable=E1126:invalid-sequence-index
            slots_per_epoch: int = get_constants().chain.slots_per_epoch
            slot_interval: int = int(get_constants().chain.interval)

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
                trigger=FinalizeExitTrigger(pubkey),
                initial_delay=init_delay,
            )

            finalize_exit_daemon.run()
