# -*- coding: utf-8 -*-

from web3.types import TxReceipt
from geodefi.globals import VALIDATOR_STATE
from src.classes import Trigger, Database
from src.helpers.db_validators import (
    create_validators_table,
    save_local_state,
    save_portal_state,
)
from src.globals import CONFIG
from src.helpers.portal import get_StakeParams
from src.actions.portal import call_stake
from src.utils import multithread

pools_table: str = CONFIG.database.tables.pools.name


class StakeTrigger(Trigger):
    """
    Every X hours checks for approved proposals.
    Finalizes the validator creation by calling portal.stake()
    """

    name: str = "STAKE_TRIGGER"

    def __init__(self):
        """Initializes the configured trigger."""
        Trigger.__init__(self, name=self.name, action=self.activate_validators)
        create_validators_table()

    def activate_validators(self, *args, **kwargs):
        """
        Checks for approved pending validator proposals and activates them by staking.

        Args:
            events(int) : sorted list of Delegation emits
        """
        # TODO add flag for --min_proposal_queue --max-proposal-delay etc.
        verification_index: int = get_StakeParams()[4]

        # check if there are any pending validator proposals.
        with Database() as db:
            db.execute(
                f"""
                    SELECT pubkey FROM {pools_table} 
                    WHERE internal_state = {VALIDATOR_STATE.PROPOSED}  
                    AND portal_index < {verification_index}
                """
            )

            approved_pks: list[str] = db.fetchall()

            # todo : handle tx receipt
            tx_receipt: TxReceipt = call_stake(approved_pks)

            # update db after a succesful call
            multithread(save_local_state, approved_pks, VALIDATOR_STATE.ACTIVE)
            multithread(save_portal_state, approved_pks, VALIDATOR_STATE.ACTIVE)
