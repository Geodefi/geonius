# -*- coding: utf-8 -*-

import sys
from typing import Any, Iterable
from web3.types import EventData
from geodefi.globals import VALIDATOR_STATE
from geodefi.classes import Validator

from src.classes import Trigger, Database
from src.daemons import TimeDaemon
from src.exceptions import BeaconStateMismatchError, DatabaseError, EthdoError
from src.globals import SDK, CONFIG
from src.helpers import (
    create_exit_request_table,
    event_handler,
    save_portal_state,
    save_local_state,
    save_exit_epoch,
    run_finalize_exit_triggers,
    check_pk_in_db,
)
from src.actions import exit_validator

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
        saveable_events: list[tuple] = []
        for event in events:
            pubkey: int = event.args.pubkey
            block_number: int = event.blockNumber
            transaction_index: int = event.transactionIndex
            log_index: int = event.logIndex

            saveable_events.append(
                (
                    pubkey,
                    block_number,
                    transaction_index,
                    log_index,
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

            # TODO: if this is not waiting for tx to be mined, there should be a way to handle and check the beacon_status
            try:
                exit_validator(pubkey)
            except EthdoError as e:
                # TODO: send mail
                continue

            val: Validator = SDK.portal.validator(pubkey)
            # TODO: check what the expected status below should be in the beacon chain
            if val.beacon_status == "exiting":
                # write database the expected exit block
                save_exit_epoch(pubkey, val.exit_epoch)
                exitted_pks.append(pubkey)
            else:
                raise BeaconStateMismatchError(f"Beacon state mismatch for pubkey {pubkey}")

        # TODO: if exit_validator function (ethdo) is waiting for finalization, we do not need to
        #       seperate the for loops and we can continue under the same loop
        for pubkey in exitted_pks:
            save_local_state(pubkey, VALIDATOR_STATE.EXIT_REQUESTED)

            finalize_exit_trigger: FinalizeExitTrigger = FinalizeExitTrigger(pubkey)

            # TODO: calculate initial delay related to the exit_epoch and the current block number and set it here
            finalize_exit_deamon: TimeDaemon = TimeDaemon(
                interval=int(CONFIG.chains[SDK.network.name].interval) + 1,
                trigger=finalize_exit_trigger,
                initial_delay=val.exit_epoch,
            )

            finalize_exit_deamon.run()
