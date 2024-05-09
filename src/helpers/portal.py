# -*- coding: utf-8 -*-
from itertools import repeat
from geodefi.globals import ID_TYPE
from geodefi.utils import to_bytes32, get_key
from src.globals import SDK, OPERATOR_ID
from src.utils import multithread


# pylint: disable-next=invalid-name
# TODO: is return type correct? should be list[dict]? or dict? or list[Any]? Change internal docstring to reflect that.
def get_StakeParams() -> list:
    """Returns the result of portal.StakeParams function.

    Returns:
        list: list of StakeParams
    """
    return SDK.portal.functions.StakeParams().call()


# pylint: disable-next=invalid-name
def get_allIdsByType(type: ID_TYPE, index: int) -> int:
    """A helper function to call allIdsByType on Portal. Returns the ID of the given type and index.

    Args:
        type (ID_TYPE): type of the ID to be fetched.
        index (int): index of the ID to be fetched.

    Returns:
        int: ID of the given type and index.
    """

    return SDK.portal.functions.allIdsByType(type, index).call()


# related to pools >


def get_name(pool_id: int) -> str:
    """Returns the name of the pool with given ID.

    Args:
        pool_id (int): ID of the pool to fetch name for.

    Returns:
        str: Name of the pool.
    """

    return SDK.portal.functions.readBytes(pool_id, to_bytes32("NAME")).call()


def get_withdrawal_address(pool_id: int) -> str:
    """Returns the withdrawal address for given pool.

    Args:
        pool_id (int): ID of the pool to fetch withdrawal address for.

    Returns:
        str: Withdrawal address of the pool.
    """

    res = SDK.portal.functions.readAddress(pool_id, to_bytes32("withdrawalCredential")).call()

    return "0x" + res.hex()


def get_surplus(pool_id: int) -> int:
    """Returns the Ether amount that can be used to create validators for given pool, as wei.

    Args:
        pool_id (int): ID of the pool to fetch surplus for.

    Returns:
        int: Surplus of the pool in wei.
    """

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

    Args:
        pool_id (int): ID of the pool to fetch fallback operator for.

    Returns:
        int: Fallback operator ID of the pool.
    """

    return SDK.portal.functions.readUint(pool_id, to_bytes32("fallbackOperator")).call()


def get_pools_count() -> int:
    """Returns the number of current pools from Portal

    Returns:
        int: Number of pools.
    """

    return SDK.portal.functions.allIdsByTypeLength(ID_TYPE.POOL).call()


def get_all_pool_ids(start_index: int = 0) -> list[int]:
    """Returns the all current pool IDs from async Portal calls. It uses multithread to get all pool IDs.

    Args:
        start_index (int, optional): Index to start fetching pool IDs from. Default is 0.

    Returns:
        list[int]: list of pool IDs.
    """
    return multithread(
        get_allIdsByType,
        repeat(ID_TYPE.POOL),
        range(start_index, get_pools_count(), 1),
    )


# validators


def get_owned_pubkeys_count() -> int:
    """Returns the number of all validators that is owned by the operator.

    Returns:
        int: Number of validators owned by the operator.
    """
    return SDK.portal.functions.readUint(OPERATOR_ID, to_bytes32("validators")).call()


def get_owned_pubkey(index: int) -> str:
    """Returns the pubkey of given index for the operator's validator list.

    Args:
        index (int): index to look for pubkey in validators array

    Returns:
        str: Pubkey of the validator.
    """
    return SDK.portal.functions.readBytes(index, get_key(OPERATOR_ID, "operators"))


def get_all_owned_pubkeys(start_index: int = 0) -> list[str]:
    """Returns all of the validator pubkeys that is owned by the operator.

    Args:
        start_index (int, optional): Index to start fetching pubkeys from. Default is 0.

    Returns:
        list[str]: list of validator pubkeys.
    """
    return multithread(
        get_owned_pubkey,
        range(start_index, get_owned_pubkeys_count(), 1),
    )


def get_operatorAllowance(pool_id: int) -> int:
    """Returns the result of portal.operatorAllowance function.

    Args:
        pool_id (int): ID of the pool to fetch operator allowance for.

    Returns:
        int: Operator allowance for the given pool.
    """
    return SDK.portal.functions.operatorAllowance(pool_id, OPERATOR_ID).call()
