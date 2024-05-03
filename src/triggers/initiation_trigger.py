# -*- coding: utf-8 -*-

from geodefi.globals import ID_TYPE
from src.classes import Trigger
from src.helpers.db_pools import create_pools_table, fill_pools_table


class InitiationTrigger(Trigger):
    """
    Triggered when a new pool is created.
    Creates and updates a pool on db.
    """

    name: str = "INITIATION_TRIGGER"

    def __init__(self):
        """Initializes the configured trigger."""
        Trigger.__init__(self, name=self.name, action=self.insert_pool)
        create_pools_table()

    def __filter_events(self, event: dict):
        if event.args.TYPE == ID_TYPE.POOL:
            return True
        else:
            return False

    def insert_pool(self, events: list[dict], *args, **kwargs):
        """
        Creates a new pool and fills it with data
        for encountered pool ids within provided "IdInitiated" emits.

        Args:
            events(int) : sorted list of IdInitiated emits
        """

        # filter events where initiated ID is a Pool
        events_filtered: list[dict] = filter(self.__filter_events, events)
        # gather pool ids from filtered events
        pool_ids: list[int] = [x.args.id for x in events_filtered]

        fill_pools_table(pool_ids)
