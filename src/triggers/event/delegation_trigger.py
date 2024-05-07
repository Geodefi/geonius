# -*- coding: utf-8 -*-

from typing import List

from src.classes import Trigger, Database
from src.helpers.db_events import create_delegation_table, event_handler
from src.helpers.portal import get_operatorAllowance
from src.helpers.db_pools import create_pools_table, save_allowance
from src.globals import OPERATOR_ID


class DelegationTrigger(Trigger):
    """
    Triggered when a pool changes the Allowance for the operator.
    Updates the database with the latest info.
    """

    name: str = "DELEGATION_TRIGGER"

    def __init__(self):
        """Initializes the configured trigger."""
        Trigger.__init__(self, name=self.name, action=self.update_allowance)
        create_pools_table()
        create_delegation_table()

    def __filter_events(self, event: dict) -> bool:
        if event.args.operatorId == OPERATOR_ID:
            return True
        else:
            return False

    def __parse_events(self, events: List[dict]) -> List[tuple]:
        """Parses the events and returns a list of tuples.

        Args:
            events(list[dict]) : list of Delegation emits

        Returns:
            List[tuple] : list of saveable events
        """

        saveable_events: List[tuple] = []
        for event in events:
            pool_id: int = event.args.poolId
            operator_id: str = event.args.operatorId
            allowance: int = event.args.allowance
            block_number: int = event.blockNumber
            block_hash: str = event.blockHash
            log_index: int = event.logIndex
            transaction_index: int = event.transactionIndex
            transaction_hash: str = event.transactionHash
            address: str = event.address

            saveable_events.append(
                (
                    pool_id,
                    operator_id,
                    allowance,
                    block_number,
                    block_hash,
                    log_index,
                    transaction_index,
                    transaction_hash,
                    address,
                )
            )

        return saveable_events

    def __save_events(self, events: List[tuple]):
        """Saves the parsed events to the database.

        Args:
            events(List[tuple]) : arranged list of Delegation emits as tuples
        """

        with Database() as db:
            db.executemany(
                f"INSERT INTO delegation VALUES (?,?,?,?,?,?,?,?,?)",
                events,
            )

    def update_allowance(self, events: list[dict], *args, **kwargs):
        """
        Updates the allowance for given pool that is granted to script's OPERATOR_ID.
        for encountered pool ids within provided "Delegation" emits.

        Args:
            events(int) : sorted list of Delegation emits
        """

        # filter, parse and save events
        filtered_events: List[dict] = event_handler(
            events,
            self.__parse_events,
            self.__save_events,
            self.__filter_events,
        )

        # gather pool ids from filtered events
        pool_ids: List[int] = [x.args.poolId for x in filtered_events]

        # update db
        for pool in pool_ids:
            allowance: int = get_operatorAllowance(pool)
            save_allowance(pool, allowance)

        # TODO: Check if you can propose any new validators call check_and_propose function
