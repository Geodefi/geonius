from web3.types import TxReceipt
from src.globals import SDK, OPERATOR_ID


# pylint: disable-next=invalid-name
def call_proposeStake(
    pool_id: int,
    pubkeys: list,
    sig1s: list,
    sig31s: list,
):
    """_summary_

    Args:
        pool_id (int): pool id to propose new validators
        pubkeys (list): list of pubkeys that will be proposed for given pool_id
        sig1s (list): corresponding sigs to be used when initiating the validator with 1 ETH
        sig31 (list): corresponding sigs to be used when activating the validator WİTH 31 ETH

    Returns:
        TxReceipt: receipt of the stake calli returned to be handled accordingly
    """

    tx_hash = SDK.portal.functions.call_proposeStake(
        pool_id, OPERATOR_ID, pubkeys, sig1s, sig31s
    ).transact({"from": SDK.w3.eth.defaultAccount})

    # Wait for the transaction to be mined, and get the transaction receipt
    tx_receipt = SDK.portal.w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def call_stake(pubkeys: list[str]) -> TxReceipt:
    """
    Transact on stake function with given pubkeys, activating the approved validators.

    Returns:
        TxReceipt: receipt of the stake calli returned to be handled accordingly
    """

    try:
        if len(pubkeys) > 0:
            # confirm all approves canStake before calling stake

            for key in pubkeys:
                if not SDK.portal.functions.canStake(key).call():
                    # again placeholder, maybe pass or update the db and try again?
                    raise Exception

            tx_hash = SDK.portal.functions.stake(pubkeys).transact(
                {"from": SDK.w3.eth.defaultAccount}
            )

            # Wait for the transaction to be mined, and get the transaction receipt
            tx_receipt = SDK.portal.w3.eth.wait_for_transaction_receipt(tx_hash)
            return tx_receipt

    except Exception as e:
        raise e
