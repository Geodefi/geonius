# -*- coding: utf-8 -*-

from typing import List, Iterable
from web3.types import EventData

from geodefi.globals import ID_TYPE
from src.classes import Trigger, Database
from src.helpers.db_pools import create_pools_table, fill_pools_table
from helpers.db_events import create_initiation_table, event_handler


class InitiationTrigger(Trigger):
    """Triggered when a new pool is created. Creates and updates a pool on db.

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: INITIATION_TRIGGER)
    """

    name: str = "INITIATION_TRIGGER"

    def __init__(self) -> None:
        """Initializes a InitiationTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.insert_pool)
        create_pools_table()
        create_initiation_table()

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

    def __parse_events(self, events: Iterable[EventData]) -> List[tuple]:
        """Parses the events to saveable format. Returns a list of tuples. Each tuple represents a saveable event.

        Args:
            events (Iterable[EventData]): List of Initiation emits

        Returns:
            List[tuple]: List of saveable events
        """

        saveable_events: List[tuple] = []
        for event in events:
            pool_id: int = event.args.id
            block_number: int = event.blockNumber
            transaction_index: int = event.transactionIndex
            log_index: int = event.logIndex
            address: str = event.address

            saveable_events.append(
                (
                    pool_id,
                    block_number,
                    log_index,
                    transaction_index,
                    address,
                )
            )

        return saveable_events

    def __save_events(self, events: List[tuple]) -> None:
        """Saves the parsed events to the database.

        Args:
            events (List[tuple]): List of Initiation emits
        """

        with Database() as db:
            db.execute(f"INSERT INTO initiation VALUES (?,?,?,?,?,?,?)", events)

    def insert_pool(self, events: Iterable[EventData], *args, **kwargs) -> None:
        """Creates a new pool and fills it with data
        for encountered pool ids within provided "IdInitiated" emits.

        Args:
            events (Iterable[EventData]): List of events
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """

        filtered_events: Iterable[EventData] = event_handler(
            events,
            self.__parse_events,
            self.__save_events,
            self.__filter_events,
        )

        # gather pool ids from filtered events
        pool_ids: List[int] = [x.args.id for x in filtered_events]

        fill_pools_table(pool_ids)
