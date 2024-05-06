# -*- coding: utf-8 -*-

from src.classes import Trigger
from src.globals import OPERATOR_ID
from src.helpers.db_events import create_fallback_table
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

    def update_fallback_operator(self, events: list[dict], *args, **kwargs):
        """
        Checks if the fallback operator is set as script's OPERATOR_ID
        for encountered pool ids within provided "FallbackOperator" emits.

        Args:
            events(int) : sorted list of FallbackOperator emits
        """

        # filter events where operator_id matches
        events_filtered: list[dict] = filter(self.__filter_events, events)
        # TODO: for all event triggers: filter + parse + save_db => handler
        # events = event_handler(filter_events(),parse_events(),save_events()) => do this to all event triggers

        # gather pool ids from filtered events
        pool_ids: list[int] = [x.args.poolId for x in events_filtered]

        for pool in pool_ids:
            fallback: int = get_fallback_operator(pool)

            # check if the fallback id is OPERATOR_ID
            # if so, column value is set to 1, sqlite3 don't do booleans
            save_fallback_operator(pool, fallback == OPERATOR_ID)

        # TODO: Check if you can propose any new validators call check_and_propose function
