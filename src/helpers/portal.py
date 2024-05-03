# -*- coding: utf-8 -*-
from itertools import repeat
from geodefi.globals import ID_TYPE
from geodefi.utils import to_bytes32, get_key
from src.globals import SDK, OPERATOR_ID
from src.utils import multithread


# pylint: disable-next=invalid-name
def get_StakeParams() -> list:
    return SDK.portal.functions.StakeParams().call()


# pylint: disable-next=invalid-name
def get_allIdsByType(type: ID_TYPE, index: int):
    """A helper function to call allIdsByType on Portal."""

    return SDK.portal.functions.allIdsByType(type, index).call()


# related to pools >


def get_name(pool_id: int) -> int:
    """Returns the Ether amount that can be used to create validators for given pool, as wei."""

    return SDK.portal.functions.readUint(id, to_bytes32("NAME")).call()


def get_withdrawal_address(pool_id: int) -> int:
    """Returns the Ether amount that can be used to create validators for given pool, as wei."""

    res = SDK.portal.functions.readAddress(
        pool_id, to_bytes32("withdrawalCredential")
    ).call()

    return "0x" + res.hex()


def get_surplus(pool_id: int) -> int:
    """Returns the Ether amount that can be used to create validators for given pool, as wei."""

    return SDK.portal.functions.readUint(pool_id, to_bytes32("surplus")).call()


# Using the get_operatorAllowance function instead now.
# def get_allowance(pool_id: int) -> int:
#     """
#     Returns Allowance.
#     """
#     return SDK.portal.functions.readUint(
#         pool_id, get_key(int(OPERATOR_ID), "allowance")
#     ).call()


def get_fallback_operator(pool_id: int) -> int:
    """Returns the fallbackOperator for given pool.
    Fallback Operators can create validators without approval.
    """

    return SDK.portal.functions.readUint(pool_id, to_bytes32("fallbackOperator")).call()


def get_pools_count():
    """Returns the number of current pools from Portal"""

    return SDK.portal.functions.allIdsByTypeLength(ID_TYPE.POOL).call()


def get_all_pool_ids(start_index: int = 0) -> int:
    """Returns the number of current pools from async Portal calls

    Args:
        start_index(int) : first index that will be looking for pool id.
    """
    return multithread(
        get_allIdsByType,
        repeat(ID_TYPE.POOL),
        range(start_index, get_pools_count(), 1),
    )


# validators


def get_owned_pubkeys_count() -> int:
    """
    Returns the number of all validators that is owned by the operator.
    """
    return SDK.portal.functions.readUint(OPERATOR_ID, to_bytes32("validators")).call()


def get_owned_pubkey(index: int) -> str:
    """Returns the pubkey of given index for the operator's validator list.

    Args:
        index (int): index to look for pubkey on validators array
    """
    return SDK.portal.functions.readBytes(index, get_key(OPERATOR_ID, "operators"))


def get_all_owned_pubkeys(start_index: int = 0) -> list:
    """
    Returns all of the validator pubkeys that is owned by the operator.
    """
    return multithread(
        get_owned_pubkey,
        range(start_index, get_owned_pubkeys_count(), 1),
    )


def get_operatorAllowance(pool_id: int) -> int:
    """Returns the result of portal.operatorAllowance function."""
    return SDK.portal.functions.operatorAllowance(pool_id, OPERATOR_ID).call()
