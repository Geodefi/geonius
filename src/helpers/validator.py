# -*- coding: utf-8 -*-

from web3.types import TxReceipt
from geodefi.globals import DEPOSIT_SIZE
from geodefi.utils import to_bytes32
from src.classes.database import Database
from src.globals import CONFIG, SDK, OPERATOR_ID
from src.actions import generate_deposit_data, call_proposeStake, call_stake
from src.helpers import get_withdrawal_address


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

            # considering the wallet balance of the operator since it might not be enough (1 eth per val)
            wallet_balance = SDK.portal.functions.readUint(
                OPERATOR_ID, to_bytes32("wallet")
            ).call()
            eth_per_wallet_balance = wallet_balance // DEPOSIT_SIZE.PROPOSAL

            return min(allowance, eth_per_prop, eth_per_wallet_balance)
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

    # TODO: current implementation is not considering last bunch of
    #       validators count is higher than threshold or not may
    #       need to implement a check for that later if needed.
    txs: list[tuple] = []
    for i in range(0, len(pubkeys), 50):
        temp_pks: list[str] = pubkeys[i : i + 50]
        temp_sigs1: list[str] = signatures1[i : i + 50]
        temp_sigs31: list[str] = signatures31[i : i + 50]

        # TODO: handle tx receipt and errors
        tx_receipt: TxReceipt = call_proposeStake(
            pool_id, temp_pks, temp_sigs1, temp_sigs31
        )
        txs.append((tx_receipt, temp_pks))

    return txs


def check_and_stake(pks: list[str]) -> list[tuple]:
    """Stake for given pubkey if able to

    Args:
        pks(list[str]) : pubkeys to stake for

    Returns:
        list[tuple] : list of tuples containing tx_receipt and pks
    """

    # TODO: current implementation is not considering last bunch of
    #       validators count is higher than threshold or not may
    #       need to implement a check for that later if needed.
    txs: list[tuple] = []
    for i in range(0, len(pks), 50):
        temp_pks: list[str] = pks[i : i + 50]
        tx_receipt: TxReceipt = call_stake(temp_pks)
        txs.append((tx_receipt, temp_pks))

    return txs
