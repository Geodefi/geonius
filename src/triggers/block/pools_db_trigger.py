# -*- coding: utf-8 -*-

from typing import List
from src.classes import Trigger
from src.helpers.portal import get_all_pool_ids
from src.helpers.db_pools import (
    reinitialize_pools_table,
    fill_pools_table,
    create_pools_table,
)


class PoolsDBTrigger(Trigger):
    """This Trigger updates all the information on Pools table.
    Database Triggers should be created before others.
    Should not be called frequently.

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: POOLS_DB_TRIGGER)
    """

    name: str = "POOLS_DB_TRIGGER"

    def __init__(self) -> None:
        """Initializes a PoolsDBTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.update_db)
        create_pools_table()

    def update_db(self, *args, **kwargs) -> None:
        """Updates all of the information on database for every pool.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """

        reinitialize_pools_table()

        ids: List[int] = get_all_pool_ids()
        fill_pools_table(ids)
