# -*- coding: utf-8 -*-

from web3.types import TxReceipt
from web3.exceptions import TimeExhausted
from src.globals import SDK, OPERATOR_ID, PRIVATE_KEY
from src.exceptions import CannotStakeError, CallFailedError
from src.logger import log
from src.utils import send_email, get_gas


def tx_params() -> dict:
    # priority_fee, base_fee = get_gas()
    # if priority_fee and base_fee:
    #     return {
    #         "from": SDK.w3.eth.defaultAccount.address,
    #         "maxPriorityFeePerGas": priority_fee,
    #         "maxFeePerGas": base_fee,
    #     }
    # else:
    #     return {
    #         "from": SDK.w3.eth.defaultAccount.address,
    #     }

    address: str = SDK.w3.eth.defaultAccount.address
    nonce: int = SDK.w3.eth.getTransactionCount(address)

    return {
        "from": address,
        "nonce": nonce,
    }


# pylint: disable-next=invalid-name
def call_proposeStake(
    pool_id: int,
    pubkeys: list,
    sig1s: list,
    sig31s: list,
) -> bool:
    """Transact on proposeStake function with given pubkeys, sigs, and pool_id.

    This function initiates a transaction to propose new validators for a given pool_id.
    It takes the pool_id, a list of pubkeys, sigs for initiating the validator with 1 ETH,
    and sigs for activating the validator with 31 ETH as input parameters.

    Args:
        pool_id (int): The pool id to propose new validators.
        pubkeys (list): A list of pubkeys that will be proposed for the given pool_id.
        sig1s (list): A list of corresponding sigs to be used when initiating the validator with 1 ETH.
        sig31s (list): A list of corresponding sigs to be used when activating the validator with 31 ETH.

    Returns:
        bool: True if the proposeStake call is successful, False otherwise.

    Raises:
        TimeExhausted: Raised if the transaction takes too long to be mined.
        CallFailedError: Raised if the proposeStake call fails.
    """

    try:
        print(f"Proposing stake for pool {pool_id} with pubkeys {pubkeys}")

        tx: dict = SDK.portal.functions.proposeStake(
            pool_id, OPERATOR_ID, pubkeys, sig1s, sig31s
        ).buildTransaction(tx_params())

        print(f"created proposeStake tx: {tx}")

        signed_tx = SDK.w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

        print(f"signed proposeStake tx: {signed_tx}")

        tx_hash: bytes = SDK.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        log.info(f"proposeStake tx is created: {tx_hash}")

        # Wait for the transaction to be mined, and get the transaction receipt
        tx_receipt: TxReceipt = SDK.portal.w3.eth.wait_for_transaction_receipt(tx_hash)
        log.info(f"proposeStake tx is concluded: {tx_receipt}")

        return True

    except TimeExhausted as e:
        log.error(f"proposeStake tx could not conclude in time.")
        raise e
    except Exception as e:
        raise CallFailedError("Failed to call proposeStake on portal contract") from e


def call_stake(pubkeys: list[str]) -> bool:
    """Transact on stake function with given pubkeys, activating the approved validators.

    This function initiates a transaction to stake the approved validators. It takes a list of
    public keys of the approved validators as input parameters. It confirms all the validators
    can stake before calling the stake function. If any of the validators cannot stake, it raises
    an exception. If all validators can stake, it initiates the transaction and returns the receipt.

    Args:
        pubkeys (list[str]): list of public keys of the approved validators.

    Returns:
        bool: True if the stake call is successful, False otherwise.

    Raises:
        CannotStakeError: Raised if any of the validators cannot stake.
        TimeExhausted: Raised if the transaction takes too long to be mined.
        CallFailedError: Raised if the stake call fails.
    """

    try:
        if len(pubkeys) > 0:
            # Confirm all approves canStake before calling stake

            for pubkey in pubkeys:
                if not SDK.portal.functions.canStake(pubkey).call():
                    log.critical(f"Not allowed to finalize staking for provided pubkey: {pubkey}")
                    raise CannotStakeError(f"Validator with pubkey {pubkey} cannot stake")

            tx_hash: str = SDK.portal.functions.stake(pubkeys).transact(tx_params())
            log.info(f"stake tx is created: {tx_hash}")

            # Wait for the transaction to be mined, and get the transaction receipt
            tx_receipt: TxReceipt = SDK.portal.w3.eth.wait_for_transaction_receipt(tx_hash)
            log.info(f"stake tx is concluded: {tx_receipt}")

            return True

    except CannotStakeError as e:
        send_email(e.__class__.__name__, str(e), [("<file_path>", "<file_name>.log")])
        return False
    except TimeExhausted as e:
        log.error(f"stake tx could not conclude in time.")
        raise e
    except Exception as e:
        raise CallFailedError("Failed to call stake on portal contract") from e
