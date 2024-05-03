# -*- coding: utf-8 -*-

from geodefi.globals import VALIDATOR_STATE
from src.classes import Database
from src.globals import SDK, CONFIG
from src.utils import multithread

validators_table: str = CONFIG.database.tables.pools.name


def create_validators_table():
    """Creates the sql database table for Pools."""

    with Database() as db:

        # fallback just records if operator is set as fallback.
        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {validators_table} (
                    portal_index INTEGER NOT NULL UNIQUE,
                    beacon_index INTEGER NOT NULL UNIQUE,
                    pubkey TEXT NOT NULL PRIMARY KEY,
                    pool_id TEXT NOT NULL PRIMARY KEY,
                    local_state TEXT NOT NULL,
                    portal_state TEXT NOT NULL,
                    signature31 INTEGER NOT NULL,
                    withdrawal_credentials TEXT NOT NULL,
                    exit_epoch INTEGER,
                )
        """
        )


def drop_validators_table():
    """Removes Pools the table from database"""

    with Database() as db:
        db.execute(f"""DROP TABLE IF EXISTS {validators_table}""")


def reinitialize_validators_table():
    """Removes validators table and creates an empty one."""

    create_validators_table()
    drop_validators_table()


def fetch_validator(pubkey: str) -> list:
    """Gathers and returns all the fresh data from chain without saving it to db."""

    val = SDK.portal.validator(pubkey)

    return {
        "portal_index": val.portal_index,  # constant
        "beacon_index": val.beacon_index,  # constant
        "pubkey": val.pubkey,  # constant
        "pool_id": val.poolId,  # constant
        "local_state": val.portal_state,
        "portal_state": val.portal_state,
        "signature31": val.signature31,  # constant
        "withdrawal_credentials": val.withdrawal_credentials,  # constant
        "exit_epoch": val.exit_epoch,  # can be set after proposal tx is mined
    }


def fetch_validators_batch(pks: list[str]) -> list:
    """Gathers and returns all the fresh data from chain without saving it to db."""
    return multithread(fetch_validator, pks)


def insert_many_validators(new_validators: list[dict]):
    """Creates a new row with given id and info for a given list of dicts."""

    with Database() as db:
        db.executemany(
            f"INSERT INTO {validators_table} VALUES (?,?,?,?,?)",
            [
                (
                    a["portal_index"],
                    a["beacon_index"],
                    a["pubkey"],
                    a["pool_id"],
                    a["local_state"],
                    a["portal_state"],
                    a["signature31"],
                    a["withdrawal_credentials"],
                    a["exit_epoch"],
                )
                for a in new_validators
            ],
        )


def fill_validators_table(pks: list[int]):
    """Updates the validators table for Operator' owned validators.

    Args:
        pks (list[int]): list of pubkeys to be filled
    """
    insert_many_validators(fetch_validators_batch(pks))


def save_local_state(pubkey: int, local_state: VALIDATOR_STATE):
    """Sets local_state on db, which will be useful in the future bebek"""

    with Database() as db:
        db.execute(
            f"""
                UPDATE {validators_table} 
                SET beacon_state = {local_state}
                WHERE pubkey = {pubkey}
            """
        )


def save_portal_state(pubkey: int, portal_state: VALIDATOR_STATE):
    """Sets portal_state on db when it changes on chain"""

    with Database() as db:
        db.execute(
            f"""
                UPDATE {validators_table} 
                SET portal_state = {portal_state}
                WHERE pubkey = {pubkey}
            """
        )
