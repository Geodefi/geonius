# -*- coding: utf-8 -*-

from typing import Any
from threading import Lock
from datetime import datetime
from geodefi.globals import DEPOSIT_SIZE, VALIDATOR_STATE, BEACON_DENOMINATOR
from geodefi.utils import to_bytes32

from src.exceptions import DatabaseMismatchError, EthdoError
from src.globals import get_sdk, get_config, get_constants, get_logger
from src.utils.notify import send_email
from src.utils.thread import multithread
from src.actions.ethdo import generate_deposit_data
from src.actions.portal import call_proposeStake, call_stake
from src.helpers.portal import (
    get_operator_allowance,
    get_surplus,
    get_withdrawal_address,
    get_name,
    can_stake,
)
from src.database.validators import save_local_state, fetch_filtered_pubkeys
from src.database.pools import save_last_proposal_timestamp


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

    allowance: int = get_operator_allowance(pool_id)

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
        get_sdk().portal.functions.readUint(get_config().operator_id, to_bytes32("wallet")).call()
    )

    get_logger().debug(
        f"Wallet balance for operator {get_name(get_config().operator_id)}: {wallet_balance}"
    )

    eth_per_wallet_balance: int = wallet_balance // (DEPOSIT_SIZE.PROPOSAL * BEACON_DENOMINATOR)

    if curr_max > eth_per_wallet_balance:
        pool_name: str = get_name(pool_id)
        get_logger().critical(
            f"Could propose {curr_max} validators for {pool_name}."
            f"But wallet only has enough funds for {eth_per_wallet_balance}"
        )
        send_email(
            "Insufficient funds for proposals",
            f"Could propose {curr_max} validators for {pool_name}."
            f"But wallet only has enough funds for {eth_per_wallet_balance}",
            dont_notify_devs=True,
        )
        return eth_per_wallet_balance

    return curr_max


def check_and_propose(pool_id: int) -> None:
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
            # This returns the length of the validators array in the contract
            # so it is same as the index of the next validator
            new_val_ind: int = (
                get_sdk()
                .portal.functions.readUint(get_config().operator_id, to_bytes32("validators"))
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
            send_email("Ethdo failed", str(e), dont_notify_devs=True)
            return []

        pubkeys: list[str] = ["0x" + prop["pubkey"] for prop in proposal_data]
        signatures1: list[str] = ["0x" + prop["signature"] for prop in proposal_data]
        signatures31: list[str] = ["0x" + prop["signature"] for prop in stake_data]

        for i in range(0, len(pubkeys), 50):
            temp_pks: list[str] = pubkeys[i : i + 50]
            temp_sigs1: list[str] = signatures1[i : i + 50]
            temp_sigs31: list[str] = signatures31[i : i + 50]

            call_proposeStake(pool_id, temp_pks, temp_sigs1, temp_sigs31)
            save_last_proposal_timestamp(
                pool_id, int(round(datetime.now().timestamp()))
            )  # why is this needed?


def check_and_stake(pks: list[str]):
    """Stake for given pubkeys if able to stake for all of them at
    once or in batches of 50 pubkeys at a time if needed to.
    Pubkeys are ordered according to their poolId to decrease gas costs.

    Args:
        pks (list[str]): pubkeys to stake for
    """
    # TODO: (later) implement "min_proposal_queue" and "max_proposal_delay"
    # under strategy for both propose and stake steps.
    # Thus allow delays on stake and proposal to save gas.
    # min_proposal_queue => min number of validators to be filled before sending a tx.
    # max_proposal_delay => max delay a proposal will wait.
    # Then, they should be grouped by the pool id to save gas as well.
    with stake_mutex:
        txs: list[list[str]] = []
        failed_pks: list[str] = []

        # Confirm all with canStake before calling stake
        confirmations: list[bool] = multithread(can_stake, pks)

        confirmed_pks: list[str] = []
        for pk, conf in zip(pks, confirmations):
            if conf:
                if len(confirmed_pks) < 50:
                    confirmed_pks.append(pk)
                else:
                    txs.append(confirmed_pks)
                    confirmed_pks = []
            else:
                get_logger().critical(f"Not allowed to finalize staking for: {pk}")
                failed_pks.append(pks)

        if txs:
            for tx in txs:
                if tx:
                    tx_hash: str = call_stake(pubkeys=tx)
                    send_email(
                        f"{len(tx)} proposals have been staked",
                        f"Here is the transaction hash:\n{tx_hash}",
                        dont_notify_devs=True,
                    )

        if failed_pks:
            f_pks: str = "\n".join(failed_pks)
            send_email(
                f"{len(failed_pks)} validator proposals have failed unexpectedly",
                f"Here is the list of validator pubkeys that have failed:\n{f_pks}",
                dont_notify_devs=True,
            )


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

        slots_per_epoch: int = 32
        slot_interval: int = int(get_constants().chain.interval)

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


def ping_pubkey_balance(pubkey: str, expected_balance: int) -> bool:
    """Checks if a validator pubkey can be reached on beaconchain.
    If it exists (not considering its status) it checks for the balance.
    Validators should be proposed in a proposeStake call previously.
    Unusually, it checks if the underlying call
    fires an error since it got 404 as a response instead of 200.

    Args:
        pubkey (str): public key of the validator to be pinged
        expected_balance (str): expected effective balance.

    Returns:
        bool: True if the validator exists on the beaconchain, False if not.
    """
    try:
        res = get_sdk().beacon.beacon_states_validators_id(state_id="head", validator_id=pubkey)
        return int(res["validator"]["balance"]) == expected_balance
    except Exception:
        return False


def ping_pubkey_status(pubkey: str, expected_status: str) -> bool:
    """Checks if a validator pubkey can be reached on beaconchain.
    If it exists, it checks if the status matches with the expected. 
    Note that, it is enough if the expected status is available as a substring.
    Validators should be proposed in a proposeStake call previously.
    Unusually, it checks if the underlying call
    fires an error since it got 404 as a response instead of 200.

    Args:
        pubkey (str): public key of the validator to be pinged
        expected_status (str): expected status of the validator.\
         pending (pending_initialized, pending_queued)\
            active
            

    Returns:
        bool: True if the validator exists on the beaconchain, False if not.
    """
    try:
        res = get_sdk().beacon.beacon_states_validators_id(state_id="head", validator_id=pubkey)
        return expected_status in str(res["status"])
    except Exception:
        return False
