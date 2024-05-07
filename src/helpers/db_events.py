# -*- coding: utf-8 -*-

from typing import Callable, List

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
                    block_number INTEGER NOT NULL
                    block_hash TEXT NOT NULL
                    log_index INTEGER NOT NULL
                    transaction_index INTEGER NOT NULL
                    transaction_hash TEXT NOT NULL
                    address TEXT NOT NULL
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
                    block_number INTEGER NOT NULL
                    block_hash TEXT NOT NULL
                    log_index INTEGER NOT NULL
                    transaction_index INTEGER NOT NULL
                    transaction_hash TEXT NOT NULL
                    address TEXT NOT NULL
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
                    block_number INTEGER NOT NULL
                    block_hash TEXT NOT NULL
                    log_index INTEGER NOT NULL
                    transaction_index INTEGER NOT NULL
                    transaction_hash TEXT NOT NULL
                    address TEXT NOT NULL
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
                    block_number INTEGER NOT NULL
                    block_hash TEXT NOT NULL
                    log_index INTEGER NOT NULL
                    transaction_index INTEGER NOT NULL
                    transaction_hash TEXT NOT NULL
                    address TEXT NOT NULL
                    FOREIGN KEY (pool_id) REFERENCES {pools_table}(id),
                    PRIMARY KEY (pool_id)
                )
        """
        )


def create_initiation_table() -> None:
    """Creates the sql database table for Initiation."""

    with Database() as db:
        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS initiation (
                    pool_id TEXT NOT NULL,
                    block_number INTEGER NOT NULL
                    block_hash TEXT NOT NULL
                    log_index INTEGER NOT NULL
                    transaction_index INTEGER NOT NULL
                    transaction_hash TEXT NOT NULL
                    address TEXT NOT NULL
                    PRIMARY KEY (pool_id)
                )
        """
        )


def event_handler(
    events: List[dict], parser: Callable, saver: Callable, filter_func: Callable = None
) -> List[dict]:
    """Handles the events by filtering, parsing and saving them.

    Args:
        events (list[dict]): List of events.
        parser (Callable): Function to parse the events.
        saver (Callable): Function to save the events.
        filter_func (Callable): Function to filter the events.
    """
    if filter_func != None:
        events: List[dict] = filter(filter_func, events)
    saveable_events = parser(events)
    saver(saveable_events)

    return events
