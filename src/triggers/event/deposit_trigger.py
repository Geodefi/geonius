# -*- coding: utf-8 -*-

from src.classes import Trigger
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
        # TODO: create event_name table

    def update_surplus(self, events: list[dict], *args, **kwargs):
        """Updates the surplus for given pool with the current data.
        for encountered pool ids within provided "Deposit" emits.

        Args:
            events(int) : sorted list of Deposit emits
        """

        # TODO: for all event triggers: filter + parse + save_db => handler
        # events = event_handler(filter_events(),parse_events(),save_events()) => do this to all event triggers
        pool_ids: list[int] = [x.args.poolId for x in events]

        for pool in pool_ids:
            surplus: int = get_surplus(pool)

            # save to db
            save_surplus(pool, surplus)

        # TODO: Check if you can propose any new validators call check_and_propose function
