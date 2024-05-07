# -*- coding: utf-8 -*-

from geodefi.globals import ID_TYPE
from src.classes import Trigger, Database
from src.helpers.db_pools import create_pools_table, fill_pools_table
from helpers.db_events import create_initiation_table, event_handler


class InitiationTrigger(Trigger):
    """
    Triggered when a new pool is created.
    Creates and updates a pool on db.
    """

    name: str = "INITIATION_TRIGGER"

    def __init__(self):
        """Initializes the configured trigger."""
        Trigger.__init__(self, name=self.name, action=self.insert_pool)
        create_pools_table()
        create_initiation_table()

    def __filter_events(self, event: dict) -> bool:
        if event.args.TYPE == ID_TYPE.POOL:
            return True
        else:
            return False

    def __parse_events(self, events: list[dict]) -> list[tuple]:
        """Parses the events and returns a list of tuples.

        Args:
            events(list[dict]) : list of IdInitiated emits

        Returns:
            List[tuple] : list of saveable events
        """

        saveable_events: list[tuple] = []
        for event in events:
            pool_id: int = event.args.id
            block_number: int = event.blockNumber
            block_hash: str = event.blockHash
            log_index: int = event.logIndex
            transaction_index: int = event.transactionIndex
            transaction_hash: str = event.transactionHash
            address: str = event.address

            saveable_events.append(
                (
                    pool_id,
                    block_number,
                    block_hash,
                    log_index,
                    transaction_index,
                    transaction_hash,
                    address,
                )
            )

        return saveable_events

    def __save_events(self, events: list[tuple]):
        """Saves the parsed events to the database.

        Args:
            events(list[tuple]) : arranged list of IdInitiated emits as tuples
        """

        with Database() as db:
            db.execute(f"INSERT INTO initiation VALUES (?,?,?,?,?,?,?)", events)

    def insert_pool(self, events: list[dict], *args, **kwargs):
        """
        Creates a new pool and fills it with data
        for encountered pool ids within provided "IdInitiated" emits.

        Args:
            events(int) : sorted list of IdInitiated emits
        """

        filtered_events: list[tuple] = event_handler(
            events,
            self.__parse_events,
            self.__save_events,
            self.__filter_events,
        )

        # gather pool ids from filtered events
        pool_ids: list[int] = [x.args.id for x in filtered_events]

        fill_pools_table(pool_ids)
