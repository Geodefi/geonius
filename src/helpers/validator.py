# -*- coding: utf-8 -*-

from web3.types import TxReceipt
from geodefi.globals import DEPOSIT_SIZE, VALIDATOR_STATE
from src.classes.database import Database
from src.globals import CONFIG
from src.actions import generate_deposit_data, call_proposeStake
from src.helpers import get_withdrawal_address
from src.utils import multithread
from src.helpers.db_validators import save_local_state, save_portal_state

validators_table: str = CONFIG.database.tables.validators.name
pools_table: str = CONFIG.database.tables.pools.name


def max_proposals_count(pool_id: int):
    """Get max number of proposals possible"""

    with Database() as db:
        db.execute(
            f"""
                SELECT allowance,surplus FROM {pools_table} 
                WHERE id = {pool_id.PROPOSED}  
            """
        )
        allowance, surplus = db.fetchall()

        if allowance > 0:
            # every 32 ether is 1 validator.
            eth_per_prop = surplus // DEPOSIT_SIZE.STAKE

            # TODO: we should also consider the wallet balance of the operator since it might not be enough (1 eth per val)
            return min(allowance, eth_per_prop)
        else:
            return 0


def check_and_propose(pool_id: int):
    """Propose new validators for given pool if able to"""

    # TODO: this function should accept some flags such as:
    max_allowed: int = max_proposals_count(pool_id)

    all_deposit_data: list[dict] = list()

    for i in range(max_allowed):
        proposal_data: list = generate_deposit_data(
            withdrawaladdress=get_withdrawal_address(pool_id),
            depositvalue=DEPOSIT_SIZE.PROPOSAL,
        )

        stake_data: list = generate_deposit_data(
            withdrawaladdress=get_withdrawal_address(pool_id),
            depositvalue=DEPOSIT_SIZE.STAKE,
        )

    pubkeys: list = [bytes.fromhex(prop.pubkey) for prop in proposal_data]
    signatures1: list = [bytes.fromhex(prop.signature) for prop in proposal_data]
    signatures31: list = [bytes.fromhex(prop.signature) for prop in stake_data]

    # TODO: handle tx receipt and errors
    tx_receipt: TxReceipt = call_proposeStake(
        pool_id, pubkeys, signatures1, signatures31
    )

    # TODO: instead of for loop use insert_many_validators function
    for pk in pubkeys:
        # TODO: save signatures31 list to the validators  db
        # there is no pubkey yet, so create a validator row on db first
        # update db after a succesful call
        multithread(
            save_local_state, pk, VALIDATOR_STATE.PROPOSED
        )  # TODO: this will be done during creation so this will be removed
        multithread(
            save_portal_state, pk, VALIDATOR_STATE.PROPOSED
        )  # TODO: this will be done during creation so this will be removed
