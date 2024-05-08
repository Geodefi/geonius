# -*- coding: utf-8 -*-

from typing import List, Iterable
from web3.types import EventData

from src.classes import Trigger, Database
from src.globals import OPERATOR_ID
from src.helpers.db_events import create_fallback_table, event_handler
from src.helpers.db_validators import fill_validators_table
from src.helpers.portal import get_fallback_operator
from src.helpers.db_pools import create_pools_table, save_fallback_operator
from src.helpers.validator import check_and_propose


class FallbackTrigger(Trigger):
    """Triggered when a pool changes it's fallback operator.
    Updates the database with the latest info.

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: FALLBACK_TRIGGER)
    """

    name: str = "FALLBACK_TRIGGER"

    def __init__(self) -> None:
        """Initializes a FallbackTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.update_fallback_operator)
        create_pools_table()
        create_fallback_table()

    def __filter_events(self, event: EventData) -> bool:
        """Filters the events to check if the event is for the script's OPERATOR_ID.

        Args:
            event (EventData): Event to be checked

        Returns:
            bool: True if the event is for the script's OPERATOR_ID, False otherwise
        """

        if event.args.operatorId == OPERATOR_ID:
            return True
        else:
            return False

    def __parse_events(self, events: Iterable[EventData]) -> List[tuple]:
        """Parses the events to saveable format. Returns a list of tuples. Each tuple represents a saveable event.

        Args:
            events (Iterable[EventData]): List of FallbackOperator emits

        Returns:
            List[tuple]: List of saveable events
        """

        saveable_events: List[tuple] = []
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

    def __save_events(self, events: List[tuple]) -> None:
        """Saves the events to the database.

        Args:
            events (List[tuple]): List of FallbackOperator emits
        """

        with Database() as db:
            db.executemany(
                f"INSERT INTO fallback VALUES (?,?,?,?,?,?,?,?)",
                events,
            )

    def update_fallback_operator(
        self, events: Iterable[EventData], *args, **kwargs
    ) -> None:
        """Checks if the fallback operator is set as script's OPERATOR_ID
        for encountered pool ids within provided "FallbackOperator" emits.

        Args:
            events (Iterable[EventData]): List of events
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """

        filtered_events: Iterable[EventData] = event_handler(
            events, self.__parse_events, self.__save_events, self.__filter_events
        )

        # gather pool ids from filtered events
        pool_ids: List[int] = [x.args.poolId for x in filtered_events]

        all_pks: List[tuple] = []
        for pool_id in pool_ids:
            # TODO: consider not checking fetching this, instead using from the filtered events
            #       and also consider saving threshold value
            fallback: int = get_fallback_operator(pool_id)

            # check if the fallback id is OPERATOR_ID
            # if so, column value is set to 1, sqlite3 don't do booleans
            save_fallback_operator(pool_id, fallback == OPERATOR_ID)

            # if able to propose any new validators do so
            txs: List[tuple] = check_and_propose(pool_id)
            for tx_tuple in txs:
                all_pks.extend(tx_tuple[1])  # tx[1] is the list of pubkeys

        if len(all_pks) > 0:
            fill_validators_table(all_pks)
