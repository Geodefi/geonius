# -*- coding: utf-8 -*-

from src.classes import Database
from src.globals import SDK, CONFIG


pools_table: str = CONFIG.database.tables.pools.name


def find_latest_event_block(event_name: str):
    # TODO: check db for given event_name
    return CONFIG.chains[SDK.network.name].first_block


def create_alienation_table() -> None:
    """Creates the sql database table for Alienation."""

    with Database() as db:
        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS alienation (
                    pk TEXT NOT NULL PRIMARY KEY,
                )
        """
        )


def create_delegation_table() -> None:
    """Creates the sql database table for Delegation."""

    with Database() as db:
        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS delegation (
                    pool_id TEXT NOT NULL,
                    operator_id TEXT NOT NULL,
                    allowance TEXT NOT NULL
                    FOREIGN KEY (pool_id) REFERENCES {pools_table}(id),
                    PRIMARY KEY (pool_id, operator_id)
                )
        """
        )


def create_deposit_table() -> None:
    """Creates the sql database table for Deposit."""

    with Database() as db:
        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS deposit (
                    pool_id TEXT NOT NULL,
                    bought_amount TEXT NOT NULL,
                    minted_amount TEXT NOT NULL,
                    FOREIGN KEY (pool_id) REFERENCES {pools_table}(id),
                    PRIMARY KEY (pool_id)
                )
        """
        )


def create_fallback_table() -> None:
    """Creates the sql database table for Fallback."""

    with Database() as db:
        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS fallback (
                    pool_id TEXT NOT NULL,
                    fallback_threshold INTEGER NOT NULL,
                    FOREIGN KEY (pool_id) REFERENCES {pools_table}(id),
                    PRIMARY KEY (pool_id)
                )
        """
        )
