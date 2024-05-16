# -*- coding: utf-8 -*-

from typing import Any, Iterable
from web3.types import EventData
from geodefi.globals import VALIDATOR_STATE
from geodefi.classes import Validator

from src.classes import Trigger, Database
from src.daemons import TimeDaemon
from src.globals import SDK, CONFIG
from src.helpers import (
    create_exit_request_table,
    event_handler,
    save_portal_state,
    save_local_state,
    save_exit_epoch,
    run_finalize_exit_triggers,
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
        Trigger.__init__(self, name=self.name, action=self.update_validators_status)
        # Runs finalize exit triggers if there are any validators to be finalized
        run_finalize_exit_triggers()
        create_exit_request_table()

    # TODO: Same filter with alienation_trigger.py so it can be refactored to a common function in helpers like folder
    def __filter_events(self, event: EventData) -> bool:
        with Database() as db:
            db.execute(
                """
                SELECT pubkey FROM Validators
                WHERE pubkey = ?
                """,
                (event.args.pubkey),
            )
            res: Any = db.fetchone()  # returns None if not found
        if res:
            return True
        else:
            return False

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

        with Database() as db:
            db.executemany(
                "INSERT INTO ExitRequest VALUES (?,?,?,?,?,?,?)",
                events,
            )

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

        for event in filtered_events:
            try:
                pubkey: str = event.args.pubkey
                save_portal_state(pubkey, VALIDATOR_STATE.EXIT_REQUESTED)

                # TODO: if this is not waiting for tx to be mined, there should be a way to handle and check the beacon_status
                exit_validator(pubkey)

                val: Validator = SDK.portal.validator(pubkey)
                # TODO: check what the expected status below should be in the beacon chain
                if val.beacon_status == "exiting":

                    # write database the expected exit block
                    save_exit_epoch(pubkey, val.exit_epoch)
                else:
                    # TODO: error case, raise exception to be closed in except catch
                    pass
            except Exception as e:
                raise e

        # TODO: if exit_validator function (ethdo) is waiting for finalization, we do not need to
        #       seperate the for loops and we can continue under the same loop
        for event in filtered_events:
            pubkey: str = event.args.pubkey

            save_local_state(pubkey, VALIDATOR_STATE.EXIT_REQUESTED)

            finalize_exit_trigger: FinalizeExitTrigger = FinalizeExitTrigger(pubkey)

            # TODO: calculate initial delay related to the exit_epoch and the current block number and set it here
            finalize_exit_deamon: TimeDaemon = TimeDaemon(
                interval=int(CONFIG.chains[SDK.network.name].interval) + 1,
                triggers=[finalize_exit_trigger],
                initial_delay=val.exit_epoch,
            )

            finalize_exit_deamon.run()
