# -*- coding: utf-8 -*-

from geodefi.globals import VALIDATOR_STATE
from src.classes import Database
from src.globals import SDK
from src.utils import multithread


def create_validators_table() -> None:
    """Creates the sql database table for Validators."""

    with Database() as db:

        # fallback just records if operator is set as fallback.
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS Validators (
                portal_index INTEGER NOT NULL UNIQUE,
                beacon_index INTEGER NOT NULL UNIQUE,
                pubkey TEXT NOT NULL PRIMARY KEY,
                pool_id TEXT NOT NULL,
                local_state TEXT NOT NULL,
                portal_state TEXT NOT NULL,
                signature31 INTEGER NOT NULL,
                withdrawal_credentials TEXT NOT NULL,
                exit_epoch INTEGER
            )
            """
        )


def drop_validators_table() -> None:
    """Removes Validators table from the database."""

    with Database() as db:
        db.execute("DROP TABLE IF EXISTS Validators")


def reinitialize_validators_table() -> None:
    """Removes validators table and creates an empty one."""

    drop_validators_table()
    create_validators_table()


def fetch_validator(pubkey: str) -> dict:
    """Fetches the data for a validator with the given pubkey. Returns the gathered data.

    Args:
        pubkey (str): public key of the validator

    Returns:
        dict: dictionary containing the validator info
    """

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


def fetch_validators_batch(pks: list[str]) -> list[dict]:
    """Fetches the data for validators within the given pks list. Returns the gathered data.

    Args:
        pks (list[str]): pubkeys that will be fetched

    Returns:
        list[dict]: list of dictionaries containing the validator info
    """

    return multithread(fetch_validator, pks)


def insert_many_validators(new_validators: list[dict]) -> None:
    """Inserts the given validators data into the database.

    Args:
        new_validators (list[dict]): list of dictionaries containing the validator info
    """

    with Database() as db:
        db.executemany(
            f"INSERT INTO Validators VALUES (?,?,?,?,?,?,?,?,?)",
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


def fill_validators_table(pks: list[int]) -> None:
    """Fills the validators table with the data of the given pubkeys.

    Args:
        pks (list[int]): pubkeys that will be fetched and inserted
    """
    insert_many_validators(fetch_validators_batch(pks))


def save_local_state(pubkey: int, local_state: VALIDATOR_STATE) -> None:
    """Sets local_state on db when it changes.

    Args:
        pubkey (int): public key of the validator
        local_state (VALIDATOR_STATE): new local state of the validator
    """

    with Database() as db:
        db.execute(
            """
                UPDATE Validators 
                SET beacon_state = ?
                WHERE pubkey = ?
            """,
            (local_state, pubkey),
        )


def save_portal_state(pubkey: int, portal_state: VALIDATOR_STATE) -> None:
    """Sets portal_state on db when it changes on chain.

    Args:
        pubkey (int): public key of the validator
        portal_state (VALIDATOR_STATE): new portal state of the validator

    """

    with Database() as db:
        db.execute(
            """
                UPDATE Validators 
                SET portal_state = ?
                WHERE pubkey = ?
            """,
            (portal_state, pubkey),
        )


def save_exit_epoch(pubkey: int, exit_epoch: str) -> None:
    """Sets exit_epoch on db when it changes on chain.

    Args:
        pubkey (int): public key of the validator
        exit_epoch (str): new exit epoch of the validator
    """

    with Database() as db:
        db.execute(
            """
            UPDATE Validators 
            SET exit_epoch = ?
            WHERE pubkey = ?
            """,
            (exit_epoch, pubkey),
        )
