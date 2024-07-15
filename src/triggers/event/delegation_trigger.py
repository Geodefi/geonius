# -*- coding: utf-8 -*-

from typing import Iterable
from web3.types import EventData

from src.globals import get_logger, get_env, get_constants
from src.classes import Trigger, Database
from src.daemons import TimeDaemon
from src.triggers.time import ExpectDepositsTrigger
from src.exceptions import DatabaseError
from src.helpers import (
    create_delegation_table,
    event_handler,
    check_and_propose,
    create_pools_table,
    create_operators_table,
)


class DelegationTrigger(Trigger):
    """Triggered when a pool changes the Allowance for the operator.
    Updates the database with the latest info by saving delegation events.

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: DELEGATION)
    """

    name: str = "DELEGATION"

    def __init__(self):
        """Initializes a DelegationTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.consider_allowance)
        create_operators_table()
        create_pools_table()
        create_delegation_table()
        get_logger().debug(f"{self.name} is initated.")

    def __filter_events(self, event: EventData) -> bool:
        """Filters the events to check if the event is for the script's OPERATOR_ID.

        Args:
            event (EventData): Event to be checked

        Returns:
            bool: True if the event is for the script's OPERATOR_ID, False otherwise
        """

        if event.args.operatorId == get_env().OPERATOR_ID:
            return True
        else:
            return False

    def __parse_events(self, events: Iterable[EventData]) -> list[tuple]:
        """Parses the events to saveable format. Returns a list of tuples. Each tuple represents a saveable event.

        Args:
            events (Iterable[EventData]): list of Delegation emits

        Returns:
            list[tuple]: list of saveable events
        """

        saveable_events: list[tuple] = []
        for event in events:
            saveable_events.append(
                (
                    str(event.args.poolId),
                    str(event.args.operatorId),
                    str(event.args.allowance),
                    event.blockNumber,
                    event.transactionIndex,
                    event.logIndex,
                )
            )

        return saveable_events

    def __save_events(self, events: list[tuple]) -> None:
        """Saves the events to the database.

        Args:
            events (list[tuple]): list of Delegation emits
        """

        try:
            with Database() as db:
                db.executemany(
                    "INSERT INTO Delegation VALUES (?,?,?,?,?,?)",
                    events,
                )
            get_logger().debug(f"Inserted {len(events)} events into Delegation table")
        except Exception as e:
            raise DatabaseError(f"Error inserting events to table Delegation") from e

    def consider_allowance(self, events: Iterable[EventData], *args, **kwargs) -> None:
        """If the allowance is changed, it proposes new validators for the pool if possible.
        If new validators are proposed, it also fills the validators table
        with the new validators data.

        Args:
            events (Iterable[EventData]): list of Delegation emits
        """

        # filter, parse and save events
        filtered_events: Iterable[EventData] = event_handler(
            events,
            self.__parse_events,
            self.__save_events,
            self.__filter_events,
        )

        # gather pool ids from filtered events
        pool_ids: list[int] = [x.args.poolId for x in filtered_events]

        all_proposed_pks: list[str] = []
        for pool_id in pool_ids:
            # if able to propose any new validators do so
            proposed_pks: list[str] = check_and_propose(pool_id)
            all_proposed_pks.extend(proposed_pks)

        if all_proposed_pks:
            all_deposits_daemon: TimeDaemon = TimeDaemon(
                interval=15 * get_constants().one_minute,
                trigger=ExpectDepositsTrigger(all_proposed_pks),
                initial_delay=12 * get_constants().one_hour,
            )
            all_deposits_daemon.run()
