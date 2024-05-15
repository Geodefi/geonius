# -*- coding: utf-8 -*-

from src.classes import Database
from src.utils import multithread
from src.globals import pools_table, OPERATOR_ID
from src.exceptions import DatabaseError

from .portal import get_surplus, get_fallback_operator


def create_pools_table() -> None:
    """Creates the sql database table for Pools.

    Raises:
        DatabaseError: Error creating Pools table
    """

    try:
        with Database() as db:
            # fallback just records if operator is set as fallback.
            db.execute(
                f"""
                    CREATE TABLE IF NOT EXISTS {pools_table} (
                        id TEXT NOT NULL PRIMARY KEY,
                        surplus TEXT ,
                        fallback INTEGER DEFAULT 0
                    )
            """
            )

    except Exception as e:
        raise DatabaseError(f"Error creating Pools table with name {pools_table}") from e


def drop_pools_table() -> None:
    """Removes Pools table from the database.

    Raises:
        DatabaseError: Error dropping Pools table
    """

    try:
        with Database() as db:
            db.execute(f"""DROP TABLE IF EXISTS {pools_table}""")
    except Exception as e:
        raise DatabaseError(f"Error dropping Pools table with name {pools_table}") from e


def reinitialize_pools_table() -> None:
    """Removes pools table and creates an empty one."""

    drop_pools_table()
    create_pools_table()


def fetch_pools_batch(ids: list[int]) -> list[dict]:
    """Fetches the data for pools within the given ids list. Returns the gathered data.

    Args:
        ids (list[int]): pool IDs that will be fetched

    Returns:
        list[dict]: list of dictionaries containing the pool info, in format of [{id: val, surplus: val,...},...]
    """

    surpluses: list[int] = multithread(get_surplus, ids)
    fallback_operators: list[int] = multithread(get_fallback_operator, ids)

    # transpose the info and insert all the pools
    pools_transposed: list[dict] = [
        {
            "id": str(id),
            "surplus": str(surplus),
            "fallback": 1 if fallback == OPERATOR_ID else 0,
        }
        for (id, surplus, fallback) in zip(ids, surpluses, fallback_operators)
    ]
    return pools_transposed


def insert_many_pools(new_pools: list[dict]) -> None:
    """Inserts the given pools data into the database.

    Args:
        new_pools (list[dict]): list of dictionaries containing the pool info, in format of [{id: val, surplus: val,...},...]

    Raises:
        DatabaseError: Error inserting many pools into table
    """

    try:
        with Database() as db:
            db.executemany(
                f"INSERT INTO {pools_table} VALUES (?,?,?)",
                [
                    (
                        a["id"],
                        a["surplus"],
                        a["fallback"],
                    )
                    for a in new_pools
                ],
            )
    except Exception as e:
        raise DatabaseError(f"Error inserting many pools into table {pools_table}") from e


def fill_pools_table(ids: list[int]) -> None:
    """Fills the pools table with the data of the given pool IDs.

    Args:
        ids (list[int]): pool IDs that will be fetched and inserted into the database
    """

    insert_many_pools(fetch_pools_batch(ids))


def save_surplus(pool_id: int, surplus: int) -> None:
    """Sets surplus of pool on database to provided value

    Args:
        pool_id (int): pool ID
        surplus (int): surplus value to be updated

    Raises:
        DatabaseError: Error updating surplus of pool
    """

    try:
        with Database() as db:
            db.execute(
                f"""
                    UPDATE {pools_table} 
                    SET surplus = {surplus}
                    WHERE Id = {pool_id}
                """
            )
    except Exception as e:
        raise DatabaseError(
            f"Error updating surplus of pool with id {pool_id} and surplus {surplus} \
                in table {pools_table}"
        ) from e


def save_fallback_operator(pool_id: int, value: bool) -> None:
    """Sets fallback of pool on database to provided value

    Args:
        pool_id (int): pool ID
        value (bool): fallback value to be updated

    Raises:
        DatabaseError: Error updating fallback of pool
    """

    try:
        with Database() as db:
            db.execute(
                f"""
                UPDATE {pools_table} 
                SET fallback = {1 if value else 0}
                WHERE Id = {pool_id}
                """
            )
    except Exception as e:
        raise DatabaseError(
            f"Error updating fallback of pool with id {pool_id} and value {value} \
                in table {pools_table}"
        ) from e
