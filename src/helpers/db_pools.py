# -*- coding: utf-8 -*-

from src.classes import Database
from src.utils import multithread
from src.globals import OPERATOR_ID
from src.logger import log
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
                """
                CREATE TABLE IF NOT EXISTS Pools (
                    id TEXT NOT NULL PRIMARY KEY,
                    fallback INTEGER DEFAULT 0
                )
                """
            )
        log.debug(f"Created a new table: Pools")
    except Exception as e:
        raise DatabaseError(f"Error creating Pools table") from e


def drop_pools_table() -> None:
    """Removes Pools table from the database.

    Raises:
        DatabaseError: Error dropping Pools table
    """

    try:
        with Database() as db:
            db.execute("""DROP TABLE IF EXISTS Pools""")
        log.debug(f"Dropped Table: Pools")
    except Exception as e:
        raise DatabaseError(f"Error dropping Pools table") from e


def reinitialize_pools_table() -> None:
    """Removes pools table and creates an empty one."""

    drop_pools_table()
    create_pools_table()


def fetch_pools_batch(ids: list[int]) -> list[dict]:
    """Fetches the data for pools within the given ids list. Returns the gathered data.

    Args:
        ids (list[int]): pool IDs that will be fetched

    Returns:
        list[dict]: list of dictionaries containing the pool info, in format of [{id: val, fallback: bool,...},...]
    """
    log.debug(f"Fetching pools.")

    fallback_operators: list[int] = multithread(get_fallback_operator, ids)

    # transpose the info and insert all the pools
    pools_transposed: list[dict] = [
        {
            "id": str(id),
            "fallback": 1 if fallback == OPERATOR_ID else 0,
        }
        for (id, fallback) in zip(ids, fallback_operators)
    ]
    return pools_transposed


def insert_many_pools(new_pools: list[dict]) -> None:
    """Inserts the given pools data into the database.

    Args:
        new_pools (list[dict]): list of dictionaries containing the pool info, in format of [{id: val, surplus: val,...},...]

    Raises:
        DatabaseError: Error inserting many pools into table
    """
    log.debug(f"Inserting new pools to database.")

    try:
        with Database() as db:
            db.executemany(
                "INSERT INTO Pools VALUES (?,?)",
                [
                    (
                        a["id"],
                        a["fallback"],
                    )
                    for a in new_pools
                ],
            )
    except Exception as e:
        raise DatabaseError(f"Error inserting many pools into table Pools") from e


def fill_pools_table(ids: list[int]) -> None:
    """Fills the pools table with the data of the given pool IDs.

    Args:
        ids (list[int]): pool IDs that will be fetched and inserted into the database
    """

    insert_many_pools(fetch_pools_batch(ids))


def save_fallback_operator(pool_id: int, value: bool) -> None:
    """Sets fallback of pool on database to provided value

    Args:
        pool_id (int): pool ID
        value (bool): fallback value to be updated

    Raises:
        DatabaseError: Error updating fallback of pool
    """
    log.debug(f"Saving the fallback operator for {pool_id}")

    try:
        with Database() as db:
            db.execute(
                """
                UPDATE Pools 
                SET fallback = ?
                WHERE Id = ?
                """,
                (1 if value else 0, str(pool_id)),
            )
    except Exception as e:
        raise DatabaseError(
            f"Error updating fallback of pool with id {pool_id} and value {value} \
                in table Pools"
        ) from e
