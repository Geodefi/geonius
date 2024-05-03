# -*- coding: utf-8 -*-

from itertools import repeat
from eth_abi import abi
from geodefi.utils.wrappers import multiple_attempt
from src.utils import multithread
from src.globals import MAX_BLOCK_RANGE


@multiple_attempt
def get_batch_events(event, from_block: int, limit: int) -> dict:
    """Gathers the contract events for the given address within the range of fromBlock to limit

    Args:
        address(str) : contract address to be watched
        signature: event sig
        from_block: first block to cover
        limit: last block to cover
    """
    # if range is like [0,7,3] -> 0, 3, 6
    # get_batch_events would search 0-3, 3-6 and 6-9
    # but we want 0-3, 3-6, 6-7
    to_block: int = from_block + MAX_BLOCK_RANGE
    if to_block > limit:
        to_block = limit

    # @dev do not use filters instead, some providers do not support it.
    return event.get_logs(fromBlock=from_block, toBlock=to_block)


def get_all_events(event, first_block: int, last_block: int) -> list[dict]:
    """Gathers all the events within the range of first_block to last_block, making use of multithreads.

    Args:
        event: emits to be checked within given blocks: web3.contract.events.event_name()
        first_block(str): first block to include
        last_block(str): last block to cover

    Returns:
        logs(list): sorted list of all events emitted within given range
    """
    r = range(first_block, last_block, MAX_BLOCK_RANGE)
    if first_block == last_block:
        r = range(first_block, first_block + 1)

    log_batches = multithread(get_batch_events, repeat(event), r, repeat(last_block))

    # convert list of list into a list
    logs = [log for batch in log_batches for log in batch]

    # note that the events should be sorted as: blockNumber->transactionIndex->logIndex
    # which persists here, so no need to sort again.
    return logs


def decode_abi(types: list, data) -> tuple:
    """Decode given data with list of solidity types

    Args:
        types(list) : list of different solidity types like Uint, Bytes Array etc.
    """

    decoded: tuple = abi.decode(types, bytes.fromhex(str(data.hex())[2:]))
    return decoded
