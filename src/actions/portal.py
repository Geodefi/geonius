# -*- coding: utf-8 -*-

from web3.types import TxReceipt
from web3.exceptions import TimeExhausted

from src.exceptions import CallFailedError
from src.globals import get_sdk, get_config, get_logger
from src.utils.notify import send_email
from src.utils.gas import get_gas


def tx_params() -> dict:

    priority_fee, base_fee = get_gas()

    if priority_fee and base_fee:
        return {
            "maxPriorityFeePerGas": priority_fee,
            "maxFeePerGas": base_fee,
        }

    return {}


# pylint: disable-next=invalid-name
def call_proposeStake(
    pool_id: int,
    pubkeys: list,
    sig1s: list,
    sig31s: list,
) -> None:
    """Transact on proposeStake function with given pubkeys, sigs, and pool_id.

    This function initiates a transaction to propose new validators for a given pool_id.
    It takes the pool_id, a list of pubkeys, sigs for initiating the validator with 1 ETH,
    and sigs for activating the validator with 31 ETH as input parameters.

    Args:
        pool_id (int): The pool id to propose new validators.
        pubkeys (list): A list of pubkeys that will be proposed for the given pool_id.
        sig1s (list): A list of corresponding sigs to be used when initiating\
            the validator with 1 ETH.
        sig31s (list): A list of corresponding sigs to be used when activating\
            the validator with 31 ETH.

    Raises:
        TimeExhausted: Raised if the transaction takes too long to be mined.
        CallFailedError: Raised if the proposeStake call fails.
    """

    try:
        get_logger().info(f"Proposing stake for pool {pool_id} with {len(pubkeys)} pubkeys")

        tx_hash = (
            get_sdk()
            .portal.functions.proposeStake(
                pool_id, get_config().operator_id, pubkeys, sig1s, sig31s
            )
            .transact(tx_params())
        )

        get_logger().etherscan("proposeStake", tx_hash)

    except TimeExhausted as e:
        get_logger().error(f"proposeStake tx could not conclude in time.")
        raise e
    except Exception as e:
        raise CallFailedError("Failed to call proposeStake on portal contract") from e


def call_stake(pubkeys: list[str]) -> str:
    """Transact on stake function with given pubkeys, activating the approved validators.

    This function initiates a transaction to stake the approved validators. It takes a list of
    public keys of the approved validators as input parameters. It confirms all the validators
    can stake before calling the stake function. If any of the validators cannot stake, it raises
    an exception. If all validators can stake, it initiates the transaction and returns the receipt.

    Args:
        pubkeys (list[str]): list of public keys of the approved validators.

    Raises:
        TimeExhausted: Raised if the transaction takes too long to be mined.
        CallFailedError: Raised if the stake call fails.

    Returns:
        str: Transaction hash
    """

    try:
        if len(pubkeys) > 0:
            tx_hash: str = get_sdk().portal.functions.stake(pubkeys).transact(tx_params())
            get_logger().etherscan("stake", tx_hash)
            return tx_hash

        else:
            return ""

    except TimeExhausted as e:
        get_logger().error(f"Stake tx could not conclude in time.")
        raise e
    except Exception as e:
        raise CallFailedError(
            "Failed to call stake on portal contract for some unknown reason."
        ) from e
