# -*- coding: utf-8 -*-
from typing import Any
from threading import Lock
from datetime import datetime
from geodefi.globals import DEPOSIT_SIZE, VALIDATOR_STATE, BEACON_DENOMINATOR
from geodefi.utils import to_bytes32
from web3.exceptions import TimeExhausted

# from src.classes import Database
from src.globals import get_sdk, get_config, get_env, get_constants, get_logger
from src.utils.notify import send_email
from src.actions.ethdo import generate_deposit_data
from src.actions.portal import call_proposeStake, call_stake

from src.exceptions import (
    # DatabaseError,
    DatabaseMismatchError,
    EthdoError,
    CallFailedError,
)

from src.helpers.portal import get_operatorAllowance, get_surplus, get_withdrawal_address, get_name
from src.database.validators import save_local_state, fetch_filtered_pubkeys
from src.database.pools import save_last_proposal_timestamp, fetch_last_proposal_timestamp
from src.database.operators import save_last_stake_timestamp, fetch_last_stake_timestamp


propose_mutex = Lock()
stake_mutex = Lock()


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

    get_logger().debug(f"Allowance for pool {get_name(pool_id)}: {allowance}")

    if allowance == 0:
        return 0

    surplus: int = get_surplus(pool_id)

    get_logger().debug(f"Surplus for pool {get_name(pool_id)}: {surplus}")

    if surplus == 0:
        return 0

    # every 32 ether is 1 validator.
    eth_per_prop: int = surplus // (DEPOSIT_SIZE.STAKE * BEACON_DENOMINATOR)

    curr_max: int = min(allowance, eth_per_prop)

    get_logger().debug(f"Current max proposals for pool {get_name(pool_id)}: {curr_max}")

    # considering the wallet balance of the operator since it might not be enough (1 eth per val)
    wallet_balance: int = (
        get_sdk().portal.functions.readUint(get_env().OPERATOR_ID, to_bytes32("wallet")).call()
    )

    get_logger().debug(
        f"Wallet balance for operator {get_name(get_env().OPERATOR_ID)}: {wallet_balance}"
    )

    eth_per_wallet_balance: int = wallet_balance // (DEPOSIT_SIZE.PROPOSAL * BEACON_DENOMINATOR)

    if curr_max > eth_per_wallet_balance:
        pool_name: str = get_name(pool_id)
        get_logger().critical(
            f"Could propose {curr_max} validators for {pool_name}. But wallet only has enough funds for {eth_per_wallet_balance}"
        )
        send_email(
            "Insufficient funds for proposals",
            f"Could propose {curr_max} validators for {pool_name}. But wallet only has enough funds for {eth_per_wallet_balance}",
            dont_notify_devs=True,
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
    with propose_mutex:
        max_allowed: int = max_proposals_count(pool_id)

        get_logger().debug(f"Max allowed proposals for pool {get_name(pool_id)}: {max_allowed}")

        if max_allowed == 0:
            return []

        try:
            # This returns the length of the validators array in the contract so it is same as the index of the next validator
            new_val_ind: int = (
                get_sdk()
                .portal.functions.readUint(get_env().OPERATOR_ID, to_bytes32('validators'))
                .call()
            )

            for i in range(max_allowed):

                proposal_data: list[Any] = generate_deposit_data(
                    withdrawal_address=get_withdrawal_address(pool_id),
                    deposit_value=DEPOSIT_SIZE.PROPOSAL * 1_000_000_000,
                    index=new_val_ind + i,
                )

                get_logger().debug(f"Proposal data for index {new_val_ind + i}: {proposal_data}")

                stake_data: list[Any] = generate_deposit_data(
                    withdrawal_address=get_withdrawal_address(pool_id),
                    deposit_value=DEPOSIT_SIZE.STAKE * 1_000_000_000,
                    index=new_val_ind + i,
                )

                get_logger().debug(f"Stake data for index {new_val_ind + i}: {proposal_data}")

        except EthdoError as e:
            send_email(e.__class__.__name__, str(e), dont_notify_devs=True)
            return []

        # pubkeys: list[bytes] = [bytes.fromhex(prop["pubkey"]) for prop in proposal_data]
        # signatures1: list[bytes] = [bytes.fromhex(prop["signature"]) for prop in proposal_data]
        # signatures31: list[bytes] = [bytes.fromhex(prop["signature"]) for prop in stake_data]

        pubkeys: list[str] = ["0x" + prop["pubkey"] for prop in proposal_data]
        signatures1: list[str] = ["0x" + prop["signature"] for prop in proposal_data]
        signatures31: list[str] = ["0x" + prop["signature"] for prop in stake_data]

        # last_proposal_timestamp: int = fetch_last_proposal_timestamp(pool_id)

        # get_logger().info(f"Last proposal timestamp for pool {pool_id}: {last_proposal_timestamp}")

        pks: list[str] = []
        for i in range(0, len(pubkeys), 50):
            temp_pks: list[str] = pubkeys[i : i + 50]
            temp_sigs1: list[str] = signatures1[i : i + 50]
            temp_sigs31: list[str] = signatures31[i : i + 50]

            # if i >= len(pubkeys) - get_config().strategy.min_proposal_queue:
            #     if (
            #         get_config().strategy.max_proposal_delay
            #         >= int(round(datetime.now().timestamp())) - last_proposal_timestamp
            #     ):
            #         break

            try:
                success: bool = call_proposeStake(pool_id, temp_pks, temp_sigs1, temp_sigs31)
                save_last_proposal_timestamp(pool_id, int(round(datetime.now().timestamp())))
            except (CallFailedError, TimeExhausted) as e:
                # TODO: (now) somehow here, we should be checking if there are any succesful, from many 50 batch and handle
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
    with stake_mutex:
        last_stake_timestamp: int = fetch_last_stake_timestamp()
        pks: list[str] = []
        for i in range(0, len(pks), 50):
            temp_pks: list[str] = pks[i : i + 50]

            if i >= len(pks) - get_config().strategy.min_proposal_queue:
                if (
                    get_config().strategy.max_proposal_delay
                    >= int(round(datetime.now().timestamp())) - last_stake_timestamp
                ):
                    break

            try:
                success: bool = call_stake(temp_pks)
                save_last_stake_timestamp(int(round(datetime.now().timestamp())))
            except (CallFailedError, TimeExhausted) as e:
                # TODO: (now) somehow here, we should be checking if there are any succesful, from many 50 batch and handle
                raise e

            if success:
                pks.extend(temp_pks)

        return pks


def run_finalize_exit_triggers():
    """Run finalize exit trigger for all validators which are in EXIT_REQUESTED state"""

    pks: list[str] = fetch_filtered_pubkeys(portal_state=VALIDATOR_STATE.EXIT_REQUESTED)

    for pk, exit_epoch in pks:
        # check portal status, if it is not EXITTED or EXIT_REQUESTED raise an error
        chain_val_status: str = get_sdk().portal.validator(pk).state
        if chain_val_status not in ["EXIT_REQUESTED", "EXITTED"]:
            raise DatabaseMismatchError(
                f"Validator status mismatch in chain and database for pubkey {pk}"
            )

        # check portal status, if it is EXITTED save local state and continue
        if chain_val_status == "EXITTED":
            save_local_state(pk, VALIDATOR_STATE.EXITED)
            continue

        # calculate the delay for the daemon to run
        res: dict[str, Any] = get_sdk().beacon.beacon_headers_id("head")

        slots_per_epoch: int = get_constants().chain.slots_per_epoch
        slot_interval: int = int(get_constants().chain.interval)

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
        # finalize_exit_daemon: TimeDaemon = TimeDaemon(
        #     interval=slot_interval + 1,
        #     trigger=FinalizeExitTrigger(pk),
        #     initial_delay=init_delay,
        # )

        # finalize_exit_daemon.run()
