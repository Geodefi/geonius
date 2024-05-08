from typing import List
from web3.types import TxReceipt
from src.globals import SDK, OPERATOR_ID


# pylint: disable-next=invalid-name
def call_proposeStake(
    pool_id: int,
    pubkeys: List,
    sig1s: List,
    sig31s: List,
) -> TxReceipt:
    """Transact on proposeStake function with given pubkeys, sigs, and pool_id.

    This function initiates a transaction to propose new validators for a given pool_id.
    It takes the pool_id, a list of pubkeys, sigs for initiating the validator with 1 ETH,
    and sigs for activating the validator with 31 ETH as input parameters.

    Args:
        pool_id (int): The pool id to propose new validators.
        pubkeys (List): A list of pubkeys that will be proposed for the given pool_id.
        sig1s (List): A list of corresponding sigs to be used when initiating the validator with 1 ETH.
        sig31s (List): A list of corresponding sigs to be used when activating the validator with 31 ETH.

    Returns:
        TxReceipt: The receipt of the stake call returned to be handled accordingly.
    """

    tx_hash: str = SDK.portal.functions.call_proposeStake(
        pool_id, OPERATOR_ID, pubkeys, sig1s, sig31s
    ).transact({"from": SDK.w3.eth.defaultAccount})

    # Wait for the transaction to be mined, and get the transaction receipt
    tx_receipt: TxReceipt = SDK.portal.w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def call_stake(pubkeys: List[str]) -> TxReceipt:
    """Transact on stake function with given pubkeys, activating the approved validators.

    This function initiates a transaction to stake the approved validators. It takes a list of
    public keys of the approved validators as input parameters. It confirms all the validators
    can stake before calling the stake function. If any of the validators cannot stake, it raises
    an exception. If all validators can stake, it initiates the transaction and returns the receipt.

    Args:
        pubkeys (List[str]): List of public keys of the approved validators.

    Returns:
        TxReceipt: Receipt of the stake call returned to be handled accordingly.
    """

    try:
        if len(pubkeys) > 0:
            # Confirm all approves canStake before calling stake

            for key in pubkeys:
                if not SDK.portal.functions.canStake(key).call():
                    # Again placeholder, maybe pass or update the db and try again?
                    raise Exception

            tx_hash: str = SDK.portal.functions.stake(pubkeys).transact(
                {"from": SDK.w3.eth.defaultAccount}
            )

            # Wait for the transaction to be mined, and get the transaction receipt
            tx_receipt: TxReceipt = SDK.portal.w3.eth.wait_for_transaction_receipt(
                tx_hash
            )
            return tx_receipt

    except Exception as e:
        raise e
