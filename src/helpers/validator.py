# -*- coding: utf-8 -*-

from typing import Any
from datetime import datetime
from geodefi.globals import DEPOSIT_SIZE, VALIDATOR_STATE
from geodefi.utils import to_bytes32
from web3.exceptions import TimeExhausted

from src.classes import Database
from src.logger import log
from src.globals import SDK, OPERATOR_ID, chain, CONFIG
from src.utils import send_email
from src.actions import generate_deposit_data, call_proposeStake, call_stake
from src.daemons.time_daemon import TimeDaemon

# from src.triggers.time.finalize_exit_trigger import FinalizeExitTrigger
from src.exceptions import DatabaseError, DatabaseMismatchError, EthdoError, CallFailedError

from .portal import get_operatorAllowance, get_surplus, get_withdrawal_address
from .db_validators import fill_validators_table, save_local_state
from .db_pools import save_last_proposal_timestamp
from .db_operator import save_last_stake_timestamp


def fetch_last_proposal_timestamp(pool_id: int) -> int:
    """Fetches the last proposal timestamp for given pool

    Args:
        pool_id (int): ID of the pool to get last proposal timestamp for

    Returns:
        int: Last proposal timestamp
    """

    try:
        with Database() as db:
            db.execute(
                """
                SELECT last_proposal_ts FROM Pools
                WHERE id = ?
                """,
                (str(pool_id),),
            )
            last_proposal_ts: int = db.fetchone()[0]
    except Exception as e:
        raise DatabaseError(f"Error fetching last proposal timestamp for pool {pool_id}") from e

    return last_proposal_ts


def fetch_last_stake_timestamp() -> int:
    """Fetches the last stake timestamp for the operator

    Returns:
        int: Last stake timestamp
    """

    try:
        with Database() as db:
            db.execute(
                """
                SELECT last_stake_ts FROM Operators
                WHERE id = ?
                """,
                (str(OPERATOR_ID),),
            )
            last_stake_ts: int = db.fetchone()[0]
    except Exception as e:
        raise DatabaseError(
            f"Error fetching last stake timestamp for operator {OPERATOR_ID}"
        ) from e

    return last_stake_ts


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
    if allowance == 0:
        return 0

    surplus: int = get_surplus(pool_id)
    if surplus == 0:
        return 0

    # every 32 ether is 1 validator.
    eth_per_prop: int = surplus // DEPOSIT_SIZE.STAKE
    curr_max: int = min(allowance, eth_per_prop)

    # considering the wallet balance of the operator since it might not be enough (1 eth per val)
    wallet_balance: int = SDK.portal.functions.readUint(OPERATOR_ID, to_bytes32("wallet")).call()
    eth_per_wallet_balance: int = wallet_balance // DEPOSIT_SIZE.PROPOSAL

    if curr_max > eth_per_wallet_balance:
        log.critical(
            f"Could propose {curr_max} validators for {pool_id}. \
                But wallet only has enough funds for {eth_per_wallet_balance}"
        )
        send_email(
            "Insufficient funds for proposals",
            f"Could propose {curr_max} validators for {pool_id}. \
                But wallet only has enough funds for {eth_per_wallet_balance}",
            [("<file_path>", "<file_name>.log")],
        )
        return eth_per_wallet_balance

    else:
        return curr_max


def check_and_propose(pool_id: int) -> list[str]:
    """Propose for given pool if able to propose for all of them at once \
        or in batches of 50 pubkeys at a time if needed to.

    Args:
        pool_id (int): ID of the pool to propose for

    Returns:
        list[str]: list of pubkeys proposed
    """

    max_allowed: int = max_proposals_count(pool_id)

    if max_allowed == 0:
        return []

    try:
        # This returns the length of the validators array in the contract so it is same as the index of the next validator
        new_val_ind: int = SDK.portal.functions.readUint(OPERATOR_ID, to_bytes32('validators'))
        for i in range(max_allowed):
            proposal_data: list[Any] = generate_deposit_data(
                withdrawal_address=get_withdrawal_address(pool_id),
                deposit_value=DEPOSIT_SIZE.PROPOSAL,
                index=new_val_ind + i,
            )

            stake_data: list[Any] = generate_deposit_data(
                withdrawal_address=get_withdrawal_address(pool_id),
                deposit_value=DEPOSIT_SIZE.STAKE,
                index=new_val_ind + i,
            )
    except EthdoError as e:
        send_email(e.__class__.__name__, str(e), [("<file_path>", "<file_name>.log")])
        return []

    pubkeys: list[bytes] = [bytes.fromhex(prop.pubkey) for prop in proposal_data]
    signatures1: list[bytes] = [bytes.fromhex(prop.signature) for prop in proposal_data]
    signatures31: list[bytes] = [bytes.fromhex(prop.signature) for prop in stake_data]

    last_proposal_timestamp: int = fetch_last_proposal_timestamp(pool_id)
    pks: list[str] = []
    for i in range(0, len(pubkeys), 50):
        temp_pks: list[str] = pubkeys[i : i + 50]
        temp_sigs1: list[str] = signatures1[i : i + 50]
        temp_sigs31: list[str] = signatures31[i : i + 50]

        if i >= len(pubkeys) - CONFIG.min_proposal_queue:
            if (
                CONFIG.max_proposal_delay
                >= int(round(datetime.now().timestamp())) - last_proposal_timestamp
            ):
                break

        try:
            success: bool = call_proposeStake(pool_id, temp_pks, temp_sigs1, temp_sigs31)
            save_last_proposal_timestamp(pool_id, int(round(datetime.now().timestamp())))
        except (CallFailedError, TimeExhausted) as e:
            if len(pks) > 0:
                fill_validators_table(pks)
            raise e

        if success:
            pks.extend(temp_pks)

    return pks


def check_and_stake(pks: list[str]) -> list[str]:
    """Stake for given pubkeys if able to stake for all of them at \
        once or in batches of 50 pubkeys at a time if needed to.

    Args:
        pks (list[str]): pubkeys to stake for

    Returns:
        list[str]: list of pubkeys staked
    """

    last_stake_timestamp: int = fetch_last_stake_timestamp()
    pks: list[str] = []
    for i in range(0, len(pks), 50):
        temp_pks: list[str] = pks[i : i + 50]

        if i >= len(pks) - CONFIG.min_proposal_queue:
            if (
                CONFIG.max_proposal_delay
                >= int(round(datetime.now().timestamp())) - last_stake_timestamp
            ):
                break

        try:
            success: bool = call_stake(temp_pks)
            save_last_stake_timestamp(int(round(datetime.now().timestamp())))
        except (CallFailedError, TimeExhausted) as e:
            if len(pks) > 0:
                fill_validators_table(pks)
            raise e

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

        # calculate the delay for the daemon to run
        res: dict[str, Any] = SDK.beacon.beacon_headers_id("head")

        slots_per_epoch: int = chain.slots_per_epoch
        slot_interval: int = int(chain.interval)

        # pylint: disable=E1126:invalid-sequence-index
        current_slot: int = int(res["header"]["message"]["slot"])
        current_epoch: int = current_slot // slots_per_epoch

        if current_epoch >= exit_epoch:
            init_delay: int = 0
        else:
            epoch_diff: int = exit_epoch - current_epoch
            seconds_per_epoch: int = slots_per_epoch * slot_interval
            init_delay: int = epoch_diff * seconds_per_epoch

        # initialize and run the daemon
        # finalize_exit_trigger: FinalizeExitTrigger = FinalizeExitTrigger(pk)

        # finalize_exit_daemon: TimeDaemon = TimeDaemon(
        #     interval=slot_interval + 1,
        #     trigger=finalize_exit_trigger,
        #     initial_delay=init_delay,
        # )

        # finalize_exit_daemon.run()
