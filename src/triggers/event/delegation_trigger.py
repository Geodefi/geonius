# -*- coding: utf-8 -*-

from typing import List, Iterable
from web3.types import EventData

from src.classes import Trigger, Database
from src.helpers.db_events import create_delegation_table, event_handler
from src.helpers.portal import get_operatorAllowance
from src.helpers.validator import check_and_propose
from src.helpers.db_validators import fill_validators_table
from src.helpers.db_pools import create_pools_table, save_allowance
from src.globals import OPERATOR_ID


class DelegationTrigger(Trigger):
    """Triggered when a pool changes the Allowance for the operator.
    Updates the database with the latest info.

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: DELEGATION_TRIGGER)
    """

    name: str = "DELEGATION_TRIGGER"

    def __init__(self):
        """Initializes a DelegationTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.update_allowance)
        create_pools_table()
        create_delegation_table()

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
            events (Iterable[EventData]): List of Delegation emits

        Returns:
            List[tuple]: List of saveable events
        """

        saveable_events: List[tuple] = []
        for event in events:
            pool_id: int = event.args.poolId
            operator_id: str = event.args.operatorId
            allowance: int = event.args.allowance
            block_number: int = event.blockNumber
            transaction_index: int = event.transactionIndex
            log_index: int = event.logIndex
            address: str = event.address

            saveable_events.append(
                (
                    pool_id,
                    operator_id,
                    allowance,
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
            events (List[tuple]): List of Delegation emits
        """

        with Database() as db:
            db.executemany(
                f"INSERT INTO delegation VALUES (?,?,?,?,?,?,?,?,?)",
                events,
            )

    def update_allowance(self, events: Iterable[EventData], *args, **kwargs) -> None:
        """Updates the allowance for given pool that is granted to script's OPERATOR_ID.
        for encountered pool ids within provided "Delegation" emits. If the allowance is changed,
        it also proposes new validators for the pool if possible. If new validators are proposed,
        it also fills the validators table with the new validators data.

        Args:
            events (Iterable[EventData]): List of Delegation emits
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """

        # filter, parse and save events
        filtered_events: Iterable[EventData] = event_handler(
            events,
            self.__parse_events,
            self.__save_events,
            self.__filter_events,
        )

        # gather pool ids from filtered events
        pool_ids: List[int] = [x.args.poolId for x in filtered_events]

        all_pks: List[tuple] = []
        for pool_id in pool_ids:
            # update db
            allowance: int = get_operatorAllowance(pool_id)
            save_allowance(pool_id, allowance)

            # if able to propose any new validators do so
            txs: List[tuple] = check_and_propose(pool_id)
            for tx_tuple in txs:
                all_pks.extend(tx_tuple[1])  # tx[1] is the list of pubkeys

        if len(all_pks) > 0:
            fill_validators_table(all_pks)
