# -*- coding: utf-8 -*-

from src.classes import Trigger, Database
from src.globals import OPERATOR_ID
from src.helpers.db_events import create_fallback_table, event_handler
from src.helpers.portal import get_fallback_operator
from src.helpers.db_pools import create_pools_table, save_fallback_operator


class FallbackTrigger(Trigger):
    """
    Triggered when a pool changes it's fallback operator.
    Updates the database with the latest info.
    """

    name: str = "FALLBACK_TRIGGER"

    def __init__(self):
        """Initializes the configured trigger."""
        Trigger.__init__(self, name=self.name, action=self.update_fallback_operator)
        create_pools_table()
        create_fallback_table()

    def __filter_events(self, event: dict) -> bool:
        if event.args.operatorId == OPERATOR_ID:
            return True
        else:
            return False

    def __parse_events(self, events: list[dict]) -> list[tuple]:
        """Parses the events and returns a list of tuples.

        Args:
            events(list[dict]) : list of FallbackOperator emits

        Returns:
            List[tuple] : list of saveable events
        """

        saveable_events: list[tuple] = []
        for event in events:
            pool_id: int = event.args.poolId
            fallback_threshold: int = event.args.threshold
            block_number: int = event.blockNumber
            block_hash: str = event.blockHash
            log_index: int = event.logIndex
            transaction_index: int = event.transactionIndex
            transaction_hash: str = event.transactionHash
            address: str = event.address

            saveable_events.append(
                (
                    pool_id,
                    fallback_threshold,
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
            db.executemany(
                f"INSERT INTO fallback VALUES (?,?,?,?,?,?,?,?)",
                events,
            )

    def update_fallback_operator(self, events: list[dict], *args, **kwargs):
        """
        Checks if the fallback operator is set as script's OPERATOR_ID
        for encountered pool ids within provided "FallbackOperator" emits.

        Args:
            events(int) : sorted list of FallbackOperator emits
        """

        filtered_events: list[dict] = event_handler(
            events, self.__parse_events, self.__save_events, self.__filter_events
        )

        # gather pool ids from filtered events
        pool_ids: list[int] = [x.args.poolId for x in filtered_events]

        for pool in pool_ids:
            # TODO: consider not checking fetching this, instead using from the filtered events
            #       and also consider saving threshold value
            fallback: int = get_fallback_operator(pool)

            # check if the fallback id is OPERATOR_ID
            # if so, column value is set to 1, sqlite3 don't do booleans
            save_fallback_operator(pool, fallback == OPERATOR_ID)

        # TODO: Check if you can propose any new validators call check_and_propose function
