# -*- coding: utf-8 -*-

from typing import Iterable
from web3.types import EventData
from geodefi.globals import ID_TYPE

from src.logger import log
from src.classes import Trigger, Database
from src.exceptions import DatabaseError
from src.helpers import (
    create_pools_table,
    fill_pools_table,
    create_id_initiated_table,
    event_handler,
)


class IdInitiatedTrigger(Trigger):
    """Triggered when a new pool is created. Creates and updates a pool on db.

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: ID_INITIATED)
    """

    name: str = "ID_INITIATED"

    def __init__(self) -> None:
        """Initializes a IdInitiatedTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.insert_pool)
        create_pools_table()
        create_id_initiated_table()
        log.debug(f"{self.name} is initated.")

    def __filter_events(self, event: EventData) -> bool:
        """Filters the events to check if the event is a pool event.

        Args:
            event (EventData): Event to be checked

        Returns:
            bool: True if the event is a pool event, False otherwise
        """
        if event.args.TYPE == ID_TYPE.POOL:
            return True
        else:
            return False

    def __parse_events(self, events: Iterable[EventData]) -> list[tuple]:
        """Parses the events to saveable format. Returns a list of tuples. Each tuple represents a saveable event.

        Args:
            events (Iterable[EventData]): list of IdInitiated emits

        Returns:
            list[tuple]: list of saveable events
        """
        saveable_events: list[tuple] = []
        for event in events:
            pool_id: str = str(event.args.id)
            block_number: int = event.blockNumber
            transaction_index: int = event.transactionIndex
            log_index: int = event.logIndex

            saveable_events.append(
                (
                    pool_id,
                    block_number,
                    transaction_index,
                    log_index,
                )
            )

        return saveable_events

    def __save_events(self, events: list[tuple]) -> None:
        """Saves the parsed events to the database.

        Args:
            events (list[tuple]): list of IdInitiated emits
        """
        try:
            with Database() as db:
                db.executemany(
                    "INSERT INTO IdInitiated VALUES(?,?,?,?)",
                    events,
                )
            log.debug(f"Inserted {len(events)} events into IdInitiated table")
        except Exception as e:
            raise DatabaseError(f"Error inserting events to table IdInitiated") from e

    def insert_pool(self, events: Iterable[EventData], *args, **kwargs) -> None:
        """Creates a new pool and fills it with data
        for encountered pool ids within provided "IdInitiated" emits.

        Args:
            events (Iterable[EventData]): list of events
        """
        log.info(f"{self.name} is triggered.")

        filtered_events: Iterable[EventData] = event_handler(
            events,
            self.__parse_events,
            self.__save_events,
            self.__filter_events,
        )

        # gather pool ids from filtered events
        pool_ids: list[int] = [x.args.id for x in filtered_events]

        fill_pools_table(pool_ids)
