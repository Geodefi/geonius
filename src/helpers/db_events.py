# -*- coding: utf-8 -*-

from typing import Callable, Iterable
from web3.types import EventData

from src.classes import Database
from src.globals import SDK, CONFIG


def find_latest_event_block(event_name: str) -> int:
    """Finds the latest block number for the given event_name in the database. If not found, returns the first block number.

    Args:
        event_name (str): Name of the event.

    Returns:
        int: Latest saved block number for the given event_name.
    """

    # TODO: check db for given event_name

    return CONFIG.chains[SDK.network.name].start


def create_alienated_table() -> None:
    """Creates the sql database table for Alienated."""

    with Database() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS Alienated (
                pk TEXT NOT NULL PRIMARY KEY,
                block_number INTEGER NOT NULL,
                transaction_index INTEGER NOT NULL,
                log_index INTEGER NOT NULL
            )
            """
        )


def create_delegation_table() -> None:
    """Creates the sql database table for Delegation."""

    with Database() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS Delegation (
                pool_id TEXT NOT NULL,
                operator_id TEXT NOT NULL,
                allowance TEXT NOT NULL,
                block_number INTEGER NOT NULL,
                transaction_index INTEGER NOT NULL,
                log_index INTEGER NOT NULL,
                FOREIGN KEY (pool_id) REFERENCES Pools(id),
                PRIMARY KEY (pool_id, operator_id)
            )
            """
        )


def create_deposit_table() -> None:
    """Creates the sql database table for Deposit."""

    with Database() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS Deposit (
                pool_id TEXT NOT NULL,
                bought_amount TEXT NOT NULL,
                minted_amount TEXT NOT NULL,
                block_number INTEGER NOT NULL,
                transaction_index INTEGER NOT NULL,
                log_index INTEGER NOT NULL,
                FOREIGN KEY (pool_id) REFERENCES Pools(id),
                PRIMARY KEY (pool_id)
            )
            """
        )


def create_fallback_operator_table() -> None:
    """Creates the sql database table for FallbackOperator."""

    with Database() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS FallbackOperator (
                pool_id TEXT NOT NULL,
                fallback_threshold INTEGER NOT NULL,
                block_number INTEGER NOT NULL,
                transaction_index INTEGER NOT NULL,
                log_index INTEGER NOT NULL,
                FOREIGN KEY (pool_id) REFERENCES Pools(id),
                PRIMARY KEY (pool_id)
            )
            """
        )


def create_id_initiated_table() -> None:
    """Creates the sql database table for IdInitiated."""

    with Database() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS IdInitiated (
                pool_id TEXT NOT NULL,
                block_number INTEGER NOT NULL,
                transaction_index INTEGER NOT NULL,
                log_index INTEGER NOT NULL,
                PRIMARY KEY (pool_id)
            )
            """
        )


def create_exit_request_table() -> None:
    """Creates the sql database table for ExitRequest."""

    with Database() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS ExitRequest (
                pk TEXT NOT NULL,
                block_number INTEGER NOT NULL,
                transaction_index INTEGER NOT NULL,
                log_index INTEGER NOT NULL,
                FOREIGN KEY (pk) REFERENCES Validators(pk),
                PRIMARY KEY (pk)
            )
            """
        )


def event_handler(
    events: Iterable[EventData],
    parser: Callable,
    saver: Callable,
    filter_func: Callable = None,
) -> Iterable[EventData]:
    """Handles the events by filtering, parsing and saving them.

    Args:
        events (Iterable[EventData]): list of events.
        parser (Callable): Function to parse the events.
        saver (Callable): Function to save the events.
        filter_func (Callable, optional): Function to filter the events. Defaults to None.
    """
    if filter_func is not None:
        events: Iterable[EventData] = filter(filter_func, events)
    saveable_events: list[tuple] = parser(events)
    saver(saveable_events)

    return events
