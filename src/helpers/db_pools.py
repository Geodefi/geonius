# -*- coding: utf-8 -*-

from src.helpers.portal import get_surplus, get_operatorAllowance, get_fallback_operator
from src.classes import Database
from src.utils import multithread
from src.globals import OPERATOR_ID


def create_pools_table() -> None:
    """Creates the sql database table for Pools."""

    with Database() as db:
        # fallback just records if operator is set as fallback.
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS Pools (
                id TEXT NOT NULL PRIMARY KEY,
                surplus TEXT ,
                allowance TEXT ,
                fallback INTEGER DEFAULT 0
            )
            """
        )


def drop_pools_table() -> None:
    """Removes Pools table from the database."""

    with Database() as db:
        db.execute("DROP TABLE IF EXISTS Pools")


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
    allowances: list[int] = multithread(get_operatorAllowance, ids)
    fallback_operators: list[int] = multithread(get_fallback_operator, ids)

    # transpose the info and insert all the pools
    pools_transposed: list[dict] = [
        {
            "id": str(id),
            "surplus": str(surplus),
            "allowance": str(allowance),
            "fallback": 1 if fallback == OPERATOR_ID else 0,
        }
        for (id, surplus, allowance, fallback) in zip(
            ids, surpluses, allowances, fallback_operators
        )
    ]
    return pools_transposed


def insert_many_pools(new_pools: list[dict]) -> None:
    """Inserts the given pools data into the database.

    Args:
        new_pools (list[dict]): list of dictionaries containing the pool info, in format of [{id: val, surplus: val,...},...]
    """

    with Database() as db:
        db.executemany(
            "INSERT INTO Pools VALUES(?,?,?,?)",
            [
                (
                    a["id"],
                    a["surplus"],
                    a["allowance"],
                    a["fallback"],
                )
                for a in new_pools
            ],
        )


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
    """

    with Database() as db:
        db.execute(
            """
            UPDATE Pools 
            SET surplus = ?
            WHERE id = ?
            """,
            (surplus, pool_id),
        )


def save_fallback_operator(pool_id: int, value: bool) -> None:
    """Sets fallback of pool on database to provided value

    Args:
        pool_id (int): pool ID
        value (bool): fallback value to be updated
    """

    with Database() as db:
        db.execute(
            """
            UPDATE Pools 
            SET fallback = ?
            WHERE id = ?
            """,
            (1 if value else 0, pool_id),
        )


def save_allowance(pool_id: int, allowance: int) -> None:
    """Sets allowance for pool on database to provided value

    Args:
        pool_id (int): pool id
        allowance (int): allowance value to be updated
    """

    with Database() as db:
        db.execute(
            """
            UPDATE Pools 
            SET allowance = ?
            WHERE id = ?
            """,
            (allowance, pool_id),
        )
