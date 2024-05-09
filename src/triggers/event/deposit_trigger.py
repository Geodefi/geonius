# -*- coding: utf-8 -*-

from typing import List, Iterable
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

    def __parse_events(self, events: Iterable[EventData]) -> List[tuple]:
        """Parses the events to saveable format. Returns a list of tuples. Each tuple represents a saveable event.

        Args:
            events (Iterable[EventData]): List of Deposit emits

        Returns:
            List[tuple]: List of saveable events
        """

        saveable_events: List[tuple] = []
        for event in events:
            pool_id: int = event.args.poolId
            bought_amount: int = event.args.boughtgETH
            minted_amount: int = event.args.mintedgETH
            block_number: int = event.blockNumber
            log_index: int = event.logIndex
            transaction_index: int = event.transactionIndex
            address: str = event.address

            saveable_events.append(
                (
                    pool_id,
                    bought_amount,
                    minted_amount,
                    block_number,
                    transaction_index,
                    log_index,
                    address,
                )
            )

        return saveable_events

    def __save_events(self, events: List[tuple]) -> None:
        """Saves the events to the database.

        Args:
            events (List[tuple]): List of Deposit emits
        """

        with Database() as db:
            db.execute_many(
                f"INSERT INTO deposit VALUES (?,?,?,?,?,?,?,?,?)",
                events,
            )

    def update_surplus(self, events: Iterable[EventData], *args, **kwargs) -> None:
        """Updates the surplus for given pool with the current data.
        for encountered pool ids within provided "Deposit" emits.

        Args:
            events (Iterable[EventData]): List of events
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """

        # parse and save events
        filtered_events: Iterable[EventData] = event_handler(
            events, self.__parse_events, self.__save_events
        )

        pool_ids: List[int] = [x.args.poolId for x in filtered_events]

        all_pks: List[tuple] = []
        for pool_id in pool_ids:
            # save to db
            surplus: int = get_surplus(pool_id)
            save_surplus(pool_id, surplus)

            # if able to propose any new validators do so
            txs: List[tuple] = check_and_propose(pool_id)
            for tx_tuple in txs:
                all_pks.extend(tx_tuple[1])  # tx[1] is the list of pubkeys

        if len(all_pks) > 0:
            fill_validators_table(all_pks)
