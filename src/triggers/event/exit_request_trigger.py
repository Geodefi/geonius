# -*- coding: utf-8 -*-

from typing import Any, List, Iterable
from web3.types import EventData
from geodefi.globals import VALIDATOR_STATE
from src.classes import Trigger, Database
from src.globals import CONFIG
from src.helpers.db_events import create_exit_request_table, event_handler
from src.helpers.db_validators import (
    create_validators_table,
    save_portal_state,
    save_local_state,
)

# TODO: need to be refactered after merged with other branch, need to fetch it from globals.constants
validators_table: str = CONFIG.database.tables.pools.name


class ExitRequestTrigger(Trigger):
    name: str = "EXIT_REQUEST_TRIGGER"

    def __init__(self) -> None:
        Trigger.__init__(self, name=self.name, action=self.alienate_validators)
        create_exit_request_table()

    # TODO: Same filter with alienation_trigger.py so it can be refactored to a common function in helpers like folder
    def __filter_events(self, event: EventData) -> bool:
        with Database() as db:
            db.execute(
                f"""
                    SELECT pubkey FROM {validators_table}
                    WHERE pubkey = {event.args.pubkey}
                """
            )
            res: Any = db.fetchone()  # returns None if not found
        if res:
            return True
        else:
            return False

    def __parse_events(self, events: Iterable[EventData]) -> List[tuple]:
        saveable_events: List[tuple] = []
        for event in events:
            pubkey: int = event.args.pubkey
            block_number: int = event.blockNumber
            log_index: int = event.logIndex
            transaction_index: int = event.transactionIndex
            address: str = event.address

            saveable_events.append(
                (
                    pubkey,
                    block_number,
                    log_index,
                    transaction_index,
                    address,
                )
            )

        return saveable_events

    def __save_events(self, events: List[tuple]) -> None:
        """Saves the events to the database.

        Args:
            events (List[tuple]): List of saveable events
        """

        with Database() as db:
            db.executemany(
                f"INSERT INTO exit_request VALUES (?,?,?,?,?,?,?)",
                events,
            )

    def update_validators_status(
        self, events: Iterable[EventData], *args, **kwargs
    ) -> None:
        # filter, parse and save events
        filtered_events: Iterable[EventData] = event_handler(
            events,
            self.__parse_events,
            self.__save_events,
            self.__filter_events,
        )

        exit_requested_pks: List[int] = [x.args.pubkey for x in filtered_events]

        for pk in exit_requested_pks:
            save_portal_state(pk, VALIDATOR_STATE.EXIT_REQUESTED)
            save_local_state(pk, VALIDATOR_STATE.EXIT_REQUESTED)
