# -*- coding: utf-8 -*-

from typing import Any
from geodefi.globals import DEPOSIT_SIZE, VALIDATOR_STATE
from geodefi.utils import to_bytes32

from src.classes import Database
from src.globals import SDK, OPERATOR_ID, CONFIG
from src.actions import generate_deposit_data, call_proposeStake, call_stake
from src.daemons.time_daemon import TimeDaemon
from src.triggers.time.finalize_exit_trigger import FinalizeExitTrigger
from src.exceptions import DatabaseError, DatabaseMismatchError

from .portal import get_operatorAllowance, get_withdrawal_address
from .db_validators import save_local_state


def max_proposals_count(pool_id: int) -> int:
    """Returns the maximum proposals count for given pool

    Args:
        pool_id (int): ID of the pool to get max proposals count for

    Returns:
        int: Maximum possible proposals count

    Raises:
        DatabaseError: Error fetching allowance and surplus for pool from table
    """

    allowance: int = get_operatorAllowance(pool_id)
    try:
        with Database() as db:
            db.execute(
                """
                SELECT surplus FROM Pools 
                WHERE id = ?
                """,
                (pool_id),
            )
            surplus: str = db.fetchone()  # surplus is a TEXT field
            surplus = int(surplus)
    except Exception as e:
        raise DatabaseError(f"Error fetching surplus for pool {pool_id} from table Pools") from e

    if allowance > 0:
        # every 32 ether is 1 validator.
        eth_per_prop: int = int(surplus) // DEPOSIT_SIZE.STAKE

        # considering the wallet balance of the operator since it might not be enough (1 eth per val)
        wallet_balance: int = SDK.portal.functions.readUint(
            OPERATOR_ID, to_bytes32("wallet")
        ).call()
        eth_per_wallet_balance: int = wallet_balance // DEPOSIT_SIZE.PROPOSAL

        return min(allowance, eth_per_prop, eth_per_wallet_balance)
    else:
        return 0


def check_and_propose(pool_id: int) -> list[str]:
    """Propose for given pool if able to propose for all of them at once or in batches of 50 pubkeys at a time if needed to.

    Args:
        pool_id (int): ID of the pool to propose for

    Returns:
        list[str]: list of pubkeys proposed
    """

    max_allowed: int = max_proposals_count(pool_id)

    for i in range(max_allowed):
        proposal_data: list[Any] = generate_deposit_data(
            withdrawal_address=get_withdrawal_address(pool_id),
            deposit_value=DEPOSIT_SIZE.PROPOSAL,
        )

        stake_data: list[Any] = generate_deposit_data(
            withdrawal_address=get_withdrawal_address(pool_id),
            deposit_value=DEPOSIT_SIZE.STAKE,
        )

    pubkeys: list[bytes] = [bytes.fromhex(prop.pubkey) for prop in proposal_data]
    signatures1: list[bytes] = [bytes.fromhex(prop.signature) for prop in proposal_data]
    signatures31: list[bytes] = [bytes.fromhex(prop.signature) for prop in stake_data]

    # TODO: current implementation is not considering last bunch of
    #       validators count is higher than threshold or not may
    #       need to implement a check for that later if needed.
    pks: list[str] = []
    for i in range(0, len(pubkeys), 50):
        temp_pks: list[str] = pubkeys[i : i + 50]
        temp_sigs1: list[str] = signatures1[i : i + 50]
        temp_sigs31: list[str] = signatures31[i : i + 50]

        # TODO: save pks before raising error and then raise error and handle it on deamon by closing the deamon
        success: bool = call_proposeStake(pool_id, temp_pks, temp_sigs1, temp_sigs31)
        if success:
            pks.extend(temp_pks)

    return pks


def check_and_stake(pks: list[str]) -> list[str]:
    """Stake for given pubkeys if able to stake for all of them at once or in batches of 50 pubkeys at a time if needed to.

    Args:
        pks (list[str]): pubkeys to stake for

    Returns:
        list[str]: list of pubkeys staked
    """

    # TODO: current implementation is not considering last bunch of
    #       validators count is higher than threshold or not may
    #       need to implement a check for that later if needed.
    pks: list[str] = []
    for i in range(0, len(pks), 50):
        temp_pks: list[str] = pks[i : i + 50]

        # TODO: save pks before raising error and then raise error and handle it on deamon by closing the deamon
        success: bool = call_stake(temp_pks)
        if success:
            pks.extend(temp_pks)

    return pks


def run_finalize_exit_triggers():
    """Run finalize exit trigger for all validators which are in EXIT_REQUESTED state"""

    try:
        with Database() as db:
            db.execute(
                """
                SELECT pubkey,exit_epoch  FROM Validators 
                WHERE portal_state = ?
                """,
                (int(VALIDATOR_STATE.EXIT_REQUESTED),),
            )
            pks: list[str] = db.fetchall()
    except Exception as e:
        raise DatabaseError(
            f"Error fetching validators in EXIT_REQUESTED state from table Validators"
        ) from e

    for pk, exit_epoch in pks:
        # check portal status, if it is not EXITTED or EXIT_REQUESTED raise an error
        chain_val_status: str = SDK.portal.validator(pk).state
        if chain_val_status not in ["EXIT_REQUESTED", "EXITTED"]:
            raise DatabaseMismatchError(
                f"Validator status mismatch in chain and database for pubkey {pk}"
            )

        # check portal status, if it is EXITTED save local state and continue
        if chain_val_status == "EXITTED":
            save_local_state(pk, VALIDATOR_STATE.EXITED)
            continue

        # TODO: get current epoch and calculate the initial delay if epoch is passed set initial delay to 0

        finalize_exit_trigger: FinalizeExitTrigger = FinalizeExitTrigger(pk)

        # TODO: calculate initial delay related to the exit_epoch and the current block number and set it here
        finalize_exit_deamon: TimeDaemon = TimeDaemon(
            interval=int(CONFIG.chains[SDK.network.name].interval) + 1,
            trigger=finalize_exit_trigger,
            initial_delay=exit_epoch,
        )

        finalize_exit_deamon.run()
