# -*- coding: utf-8 -*-

from typing import Iterable
from web3.types import EventData

from src.classes import Trigger, Database
from src.exceptions import DatabaseError
from src.helpers.event import event_handler
from src.helpers.validator import check_and_propose
from src.globals import get_logger


class DepositTrigger(Trigger):
    """Triggered when surplus changes for a pool.
    Updates the database with the latest info.

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: DEPOSIT)
    """

    name: str = "DEPOSIT"

    def __init__(self) -> None:
        """Initializes a DepositTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.consider_deposit)
        get_logger().debug(f"{self.name} is initated.")

    def __parse_events(self, events: Iterable[EventData]) -> list[tuple]:
        """Parses the events to saveable format. Returns a list of tuples. Each tuple represents a saveable event.

        Args:
            events (Iterable[EventData]): list of Deposit emits

        Returns:
            list[tuple]: list of saveable events
        """

        saveable_events: list[tuple] = []
        for event in events:
            saveable_events.append(
                (
                    str(event.args.poolId),
                    str(event.args.boughtgETH),
                    str(event.args.mintedgETH),
                    event.blockNumber,
                    event.transactionIndex,
                    event.logIndex,
                )
            )

        return saveable_events

    def __save_events(self, events: list[tuple]) -> None:
        """Saves the events to the database.

        Args:
            events (list[tuple]): list of Deposit emits
        """
        try:
            with Database() as db:
                db.executemany(
                    "INSERT INTO Deposit VALUES (?,?,?,?,?,?)",
                    events,
                )
            get_logger().debug(f"Inserted {len(events)} events into Deposit table")
        except Exception as e:
            raise DatabaseError(f"Error inserting events to table Deposit") from e

    def consider_deposit(self, events: Iterable[EventData], *args, **kwargs) -> None:
        """Updates the surplus for given pool with the current data.
        for encountered pool ids within provided "Deposit" emits.

        Args:
            events (Iterable[EventData]): list of events
        """
        # parse and save events
        filtered_events: Iterable[EventData] = event_handler(
            events, self.__parse_events, self.__save_events
        )

        pool_ids: list[int] = [x.args.poolId for x in filtered_events]

        for pool_id in pool_ids:
            # if able to propose any new validators do so
            check_and_propose(pool_id)
