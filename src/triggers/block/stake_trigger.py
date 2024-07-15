# -*- coding: utf-8 -*-

from itertools import repeat

from geodefi.globals import VALIDATOR_STATE

from src.classes import Trigger
from src.database.validators import (
    create_validators_table,
    save_local_state,
    save_portal_state,
    fetch_verified_pks,
)
from src.database.operators import create_operators_table
from src.helpers.validator import check_and_stake
from src.globals import get_logger
from src.utils.thread import multithread


class StakeTrigger(Trigger):
    """Every X hours checks for approved proposals.
    Finalizes the validator creation by calling portal.stake()

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: STAKE)
    """

    name: str = "STAKE"

    def __init__(self) -> None:
        """Initializes a StakeTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.activate_validators)
        create_operators_table()
        create_validators_table()
        get_logger().debug(f"{self.name} is initated.")

    def activate_validators(self, *args, **kwargs) -> None:
        """Checks for approved proposals and calls portal.stake() for them. Finalizes the validator creation."""
        # check if there are any pending validator proposals.
        staked_pks: list[str] = check_and_stake(fetch_verified_pks())

        # update db after succesful call
        if len(staked_pks) > 0:
            multithread(save_local_state, staked_pks, repeat(VALIDATOR_STATE.ACTIVE))
            multithread(save_portal_state, staked_pks, repeat(VALIDATOR_STATE.ACTIVE))
