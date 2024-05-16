# -*- coding: utf-8 -*-

from itertools import repeat
from geodefi.globals import VALIDATOR_STATE

from src.classes import Trigger, Database
from src.globals import log
from src.helpers import (
    create_validators_table,
    save_local_state,
    save_portal_state,
    get_StakeParams,
    check_and_stake,
)
from src.utils import multithread


class StakeTrigger(Trigger):
    """Every X hours checks for approved proposals.
    Finalizes the validator creation by calling portal.stake()

    Attributes:
        name (str): name of the trigger to be used when logging etc. (value: STAKE_TRIGGER)
    """

    name: str = "STAKE_TRIGGER"

    def __init__(self) -> None:
        """Initializes a StakeTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.
        """

        Trigger.__init__(self, name=self.name, action=self.activate_validators)
        create_validators_table()

    def activate_validators(self, *args, **kwargs) -> None:
        """Checks for approved proposals and calls portal.stake() for them. Finalizes the validator creation.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        log.info("IM IN STAKETRIGGER BITCH")
        # TODO: utilize flags: --min-proposal-queue --max-proposal-delay
        verification_index: int = get_StakeParams()[4]

        # check if there are any pending validator proposals.
        # TODO: dicuss if keep these db interactions in this function and
        #       handle the try except here or move them to a helper function.
        with Database() as db:
            db.execute(
                """
                SELECT pubkey FROM Validators 
                WHERE local_state = ?  
                AND portal_index < ?
                ORDER BY pool_id
                """,
                (int(VALIDATOR_STATE.PROPOSED), verification_index),
            )
            approved_pks: list[str] = db.fetchall()

        staked_pks: list[str] = check_and_stake(approved_pks)

        # update db after succesful call
        if len(staked_pks) > 0:
            multithread(save_local_state, staked_pks, repeat(VALIDATOR_STATE.ACTIVE))
            multithread(save_portal_state, staked_pks, repeat(VALIDATOR_STATE.ACTIVE))
