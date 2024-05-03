# -*- coding: utf-8 -*-

from src.classes import Trigger
from src.helpers.portal import get_surplus
from src.helpers.db_pools import create_pools_table, save_surplus


class SurplusTrigger(Trigger):
    """
    Triggered when surplus changes for a pool.
    Updates the database with the latest info.
    """

    name: str = "SURPLUS_TRIGGER"

    def __init__(self):
        """Initializes the configured trigger."""
        Trigger.__init__(self, name=self.name, action=self.update_surplus)
        create_pools_table()

    def update_surplus(self, events: list[dict], *args, **kwargs):
        """
        Updates the surplus for given pool with the current data.
        for encountered pool ids within provided "Deposit" emits.

        Args:
            events(int) : sorted list of Deposit emits
        """

        pool_ids: list[int] = [x.args.poolId for x in events]

        for pool in pool_ids:
            surplus: int = get_surplus(pool)

            # save to db
            save_surplus(pool, surplus)

        # TODO Check if you can propose any new validators
