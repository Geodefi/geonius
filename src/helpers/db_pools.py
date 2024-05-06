# -*- coding: utf-8 -*-

from src.helpers.portal import get_surplus, get_operatorAllowance, get_fallback_operator
from src.classes import Database
from src.utils import multithread
from src.globals import CONFIG

# TODO: consider fixing the table name instead of using the config
#       user can change the table name in the config file and it will cause an problems
pools_table: str = CONFIG.database.tables.pools.name


def create_pools_table() -> None:
    """Creates the sql database table for Pools."""

    with Database() as db:
        # fallback just records if operator is set as fallback.
        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {pools_table} (
                    portal_index INTEGER NOT NULL UNIQUE,
                    id TEXT NOT NULL PRIMARY KEY,
                    surplus TEXT ,
                    allowance TEXT ,
                    fallback INTEGER DEFAULT 0
                )
        """
        )


def drop_pools_table() -> None:
    """Removes Pools the table from database"""

    with Database() as db:
        db.execute(f"""DROP TABLE IF EXISTS {pools_table}""")


def reinitialize_pools_table() -> None:
    """Removes pools table and creates an empty one."""

    drop_pools_table()
    create_pools_table()


def fetch_pools_batch(ids: list[int]) -> list[dict]:
    """Gathers all the fresh data from chain without saving it to db.
    Args:
        ids (list[int]): pool ids to fetch

    Returns:
        list: gathered data in format of [{portal_index,id,...},...]
    """

    surpluses: list[int] = multithread(get_surplus, ids)
    allowances: list[int] = multithread(get_operatorAllowance, ids)
    fallback_operators: list[int] = multithread(get_fallback_operator, ids)

    # transpose the info and insert all the pools
    pools_transposed: list[dict] = [
        {
            "portal_index": portal_index,
            "id": id,
            "surplus": surplus,
            "allowance": allowance,
            "fallback": fallback,
        }
        for (portal_index, id, surplus, allowance, fallback) in zip(
            ids, surpluses, allowances, fallback_operators
        )
    ]
    return pools_transposed


def insert_many_pools(new_pools: list[dict]) -> None:
    """Creates a new row with given id and info for a given list of dicts."""

    with Database() as db:
        db.executemany(
            f"INSERT INTO {pools_table} VALUES (?,?,?,?,?)",
            [
                (
                    a["portal_index"],
                    a["id"],
                    a["surplus"],
                    a["allowance"],
                    a["fallback"],
                )
                for a in new_pools
            ],
        )


def fill_pools_table(ids: list[int]) -> None:
    """Updates all the data for pools within the given ids list.

    Args:
        ids (list[int]): pool IDs that will be updated
    """

    insert_many_pools(fetch_pools_batch(ids))


def save_surplus(pool_id: int, surplus: int) -> None:
    """Sets surplus of pool on database to provided value"""

    with Database() as db:
        db.execute(
            f"""
                UPDATE {pools_table} 
                SET surplus = {surplus}
                WHERE Id = {pool_id}
            """
        )


def save_fallback_operator(pool_id: int, value: bool) -> None:
    """Sets fallback of pool on database to provided value"""

    with Database() as db:
        db.execute(
            f"""
            UPDATE {pools_table} 
            SET fallback = {1 if value else 0}
            WHERE Id = {pool_id}
            """
        )


def save_allowance(pool_id: int, allowance: int) -> None:
    """Sets allowance for pool on database to provided value"""

    with Database() as db:
        db.execute(
            f"""
                UPDATE {pools_table} 
                SET allowance = {allowance}
                WHERE Id = {pool_id}
            """
        )
