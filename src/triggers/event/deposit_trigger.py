# -*- coding: utf-8 -*-

from src.classes import Trigger, Database
from src.helpers.db_events import create_deposit_table, event_handler
from src.helpers.portal import get_surplus
from src.helpers.db_pools import create_pools_table, save_surplus


class DepositTrigger(Trigger):
    """
    Triggered when surplus changes for a pool.
    Updates the database with the latest info.
    """

    name: str = "DEPOSIT_TRIGGER"

    def __init__(self):
        """Initializes the configured trigger."""
        Trigger.__init__(self, name=self.name, action=self.update_surplus)
        create_pools_table()
        create_deposit_table()

    def __parse_events(self, events: list[dict]) -> list[tuple]:
        """Parses the events and returns a list of tuples.

        Args:
            events(list[dict]) : list of Deposit emits

        Returns:
            List[tuple] : list of saveable events
        """

        saveable_events: list[tuple] = []
        for event in events:
            pool_id: int = event.args.poolId
            bought_amount: int = event.args.boughtgETH
            minted_amount: int = event.args.mintedgETH
            block_number: int = event.blockNumber
            block_hash: str = event.blockHash
            log_index: int = event.logIndex
            transaction_index: int = event.transactionIndex
            transaction_hash: str = event.transactionHash
            address: str = event.address

            saveable_events.append(
                (
                    pool_id,
                    bought_amount,
                    minted_amount,
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
        """Saves the events to the database.

        Args:
            events(list[tuple]) : list of saveable events
        """

        with Database() as db:
            db.execute_many(
                f"INSERT INTO deposit VALUES (?,?,?,?,?,?,?,?,?)",
                events,
            )

    def update_surplus(self, events: list[dict], *args, **kwargs):
        """Updates the surplus for given pool with the current data.
        for encountered pool ids within provided "Deposit" emits.

        Args:
            events(int) : sorted list of Deposit emits
        """

        # parse and save events
        filtered_events: list[dict] = event_handler(
            events, self.__parse_events, self.__save_events
        )

        pool_ids: list[int] = [x.args.poolId for x in filtered_events]

        for pool in pool_ids:
            surplus: int = get_surplus(pool)

            # save to db
            save_surplus(pool, surplus)

        # TODO: Check if you can propose any new validators call check_and_propose function
