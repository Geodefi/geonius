# -*- coding: utf-8 -*-

from typing import Any, Callable, List
from concurrent.futures import ThreadPoolExecutor


def multithread(
    func: Callable, *args, num_threads: int = None, chunk_size: int = 1
) -> List[Any]:
    """Turn function calls into multithread with help of iterables arguments and return the results.

    Args:
        func (Callable): function to be called
        *args: arguments to be passed to the function
        num_threads (int, optional): number of threads to be used. Defaults to None.
        chunk_size (int, optional): size of the chunk. Defaults to 1.

    Returns:
        List[Any]: list of results from the function calls
    """
    with ThreadPoolExecutor(max_workers=num_threads) as pool:
        res: Any = pool.map(func, *args, chunksize=chunk_size)
    return list(res)
