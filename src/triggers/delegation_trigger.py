# -*- coding: utf-8 -*-

from src.classes import Trigger
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

    def __filter_events(self, event: dict):
        if event.args.operatorId == OPERATOR_ID:
            return True
        else:
            return False

    def update_allowance(self, events: list[dict], *args, **kwargs):
        """
        Updates the allowance for given pool that is granted to script's OPERATOR_ID.
        for encountered pool ids within provided "Delegation" emits.

        Args:
            events(int) : sorted list of Delegation emits
        """

        # filter events where operator_id matches
        events_filtered: list[dict] = filter(self.__filter_events, events)
        # gather pool ids from filtered events
        pool_ids: list[int] = [x.args.poolId for x in events_filtered]

        # update db
        for pool in pool_ids:
            allowance: int = get_operatorAllowance(pool)
            save_allowance(pool, allowance)

        # todo Check if you can propose any new validators
