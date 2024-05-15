# -*- coding: utf-8 -*-

from typing import Iterable
from web3.types import EventData

from src.classes import Trigger, Database
from src.helpers.db_events import create_deposit_table, event_handler
from src.helpers.db_validators import fill_validators_table
from src.helpers.portal import get_surplus
from src.helpers.db_pools import create_pools_table, save_surplus
from src.helpers.validator import check_and_propose


class DepositTrigger(Trigger):
    """Triggered when surplus changes for a pool.
    Updates the database with the latest info.

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: DEPOSIT_TRIGGER)
    """

    name: str = "DEPOSIT_TRIGGER"

    def __init__(self) -> None:
        """Initializes a DepositTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.update_surplus)
        create_pools_table()
        create_deposit_table()

    def __parse_events(self, events: Iterable[EventData]) -> list[tuple]:
        """Parses the events to saveable format. Returns a list of tuples. Each tuple represents a saveable event.

        Args:
            events (Iterable[EventData]): list of Deposit emits

        Returns:
            list[tuple]: list of saveable events
        """

        saveable_events: list[tuple] = []
        for event in events:
            pool_id: int = event.args.poolId
            bought_amount: int = event.args.boughtgETH
            minted_amount: int = event.args.mintedgETH
            block_number: int = event.blockNumber
            transaction_index: int = event.transactionIndex
            log_index: int = event.logIndex

            saveable_events.append(
                (
                    pool_id,
                    bought_amount,
                    minted_amount,
                    block_number,
                    transaction_index,
                    log_index,
                )
            )

        return saveable_events

    def __save_events(self, events: list[tuple]) -> None:
        """Saves the events to the database.

        Args:
            events (list[tuple]): list of Deposit emits
        """

        with Database() as db:
            db.execute_many(
                f"INSERT INTO Deposit VALUES (?,?,?,?,?,?,?,?,?)",
                events,
            )

    def update_surplus(self, events: Iterable[EventData], *args, **kwargs) -> None:
        """Updates the surplus for given pool with the current data.
        for encountered pool ids within provided "Deposit" emits.

        Args:
            events (Iterable[EventData]): list of events
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """

        # parse and save events
        filtered_events: Iterable[EventData] = event_handler(
            events, self.__parse_events, self.__save_events
        )

        pool_ids: list[int] = [x.args.poolId for x in filtered_events]

        all_proposed_pks: list[str] = []
        for pool_id in pool_ids:
            # save to db
            surplus: int = get_surplus(pool_id)
            save_surplus(pool_id, surplus)

            # if able to propose any new validators do so
            proposed_pks: list[str] = check_and_propose(pool_id)
            all_proposed_pks.extend(proposed_pks)

        if len(all_proposed_pks) > 0:
            fill_validators_table(all_proposed_pks)
