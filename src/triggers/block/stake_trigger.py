# -*- coding: utf-8 -*-

from itertools import repeat
from geodefi.globals import VALIDATOR_STATE
from src.classes import Trigger, Database
from src.helpers.db_validators import (
    create_validators_table,
    save_local_state,
    save_portal_state,
)
from src.helpers.portal import get_StakeParams
from src.helpers.validator import check_and_stake
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
        # TODO: utilize flags: --min-proposal-queue --max-proposal-delay
        verification_index: int = get_StakeParams()[4]

        # check if there are any pending validator proposals.
        with Database() as db:
            db.execute(
                f"""
                    SELECT pubkey FROM Pools 
                    WHERE internal_state = {VALIDATOR_STATE.PROPOSED}  
                    AND portal_index < {verification_index}
                    ORDER BY id
                """
            )
            approved_pks: list[str] = db.fetchall()

        # TODO: handle tx receipt & errors
        tx_receipts: list[tuple] = check_and_stake(approved_pks)

        # TODO: may need to extend tx_receipts tuples[1] (pks) in a list
        #       instead of approved_pks
        # update db after a succesful call
        multithread(save_local_state, approved_pks, repeat(VALIDATOR_STATE.ACTIVE))
        multithread(save_portal_state, approved_pks, repeat(VALIDATOR_STATE.ACTIVE))
