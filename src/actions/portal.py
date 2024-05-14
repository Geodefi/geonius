from web3.types import TxReceipt
from src.globals import SDK, OPERATOR_ID
from src.utils.error import CannotStakeError, CallStakeError, CallProposeError
from web3.exceptions import TimeExhausted


# pylint: disable-next=invalid-name
def call_proposeStake(
    pool_id: int,
    pubkeys: list,
    sig1s: list,
    sig31s: list,
) -> TxReceipt:
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
        TxReceipt: The receipt of the stake call returned to be handled accordingly.

    Raises:
        TimeExhausted: Raised if the transaction takes too long to be mined.
        CallProposeError: Raised if the proposeStake call fails.
    """

    try:
        tx_hash: str = SDK.portal.functions.proposeStake(
            pool_id, OPERATOR_ID, pubkeys, sig1s, sig31s
        ).transact({"from": SDK.w3.eth.defaultAccount})

        # Wait for the transaction to be mined, and get the transaction receipt
        tx_receipt: TxReceipt = SDK.portal.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    except TimeExhausted as e:
        raise e
    except Exception as e:
        raise CallProposeError("Failed to call proposeStake on portal contract") from e


def call_stake(pubkeys: list[str]) -> TxReceipt:
    """Transact on stake function with given pubkeys, activating the approved validators.

    This function initiates a transaction to stake the approved validators. It takes a list of
    public keys of the approved validators as input parameters. It confirms all the validators
    can stake before calling the stake function. If any of the validators cannot stake, it raises
    an exception. If all validators can stake, it initiates the transaction and returns the receipt.

    Args:
        pubkeys (list[str]): list of public keys of the approved validators.

    Returns:
        TxReceipt: Receipt of the stake call returned to be handled accordingly.

    Raises:
        CannotStakeError: Raised if any of the validators cannot stake.
        TimeExhausted: Raised if the transaction takes too long to be mined.
        CallStakeError: Raised if the stake call fails.
    """

    try:
        if len(pubkeys) > 0:
            # Confirm all approves canStake before calling stake

            for pubkey in pubkeys:
                if not SDK.portal.functions.canStake(pubkey).call():
                    # TODO: Again placeholder, maybe pass or update the db and try again?
                    raise CannotStakeError(f"Validator with pubkey {pubkey} cannot stake")

            tx_hash: str = SDK.portal.functions.stake(pubkeys).transact(
                {"from": SDK.w3.eth.defaultAccount}
            )

            # Wait for the transaction to be mined, and get the transaction receipt
            tx_receipt: TxReceipt = SDK.portal.w3.eth.wait_for_transaction_receipt(tx_hash)
            return tx_receipt

    except (CannotStakeError, TimeExhausted) as e:
        raise e
    except Exception as e:
        raise CallStakeError("Failed to call stake on portal contract") from e
