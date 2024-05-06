# -*- coding: utf-8 -*-

from src.classes import Trigger
from src.helpers.portal import get_all_pool_ids
from src.helpers.db_pools import (
    reinitialize_pools_table,
    fill_pools_table,
    create_pools_table,
)


class PoolsDBTrigger(Trigger):
    """
    This Trigger updates all the information on Pools table.
    Database Triggers should be created before others.
    Should not be called frequently.
    """

    name: str = "POOLS_DB_TRIGGER"

    def __init__(self):
        """Initializes the configured trigger."""
        Trigger.__init__(self, name=self.name, action=self.update_db)
        create_pools_table()

    def update_db(self, *args, **kwargs):
        """Updates all of the information on database for every pool."""

        reinitialize_pools_table()

        ids: list[int] = get_all_pool_ids()
        fill_pools_table(ids)
