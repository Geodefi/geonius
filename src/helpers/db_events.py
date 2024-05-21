# -*- coding: utf-8 -*-

from typing import Callable, Iterable
from web3.types import EventData

from src.classes import Database
from src.globals import SDK, CONFIG, log
from src.exceptions import DatabaseError


def find_latest_event_block(event_name: str) -> int:
    """Finds the latest block number for the given event_name in the database. \
        If not found, returns the first block number.

    Args:
        event_name (str): Name of the event.

    Returns:
        int: Latest saved block number for the given event_name. If not found, \
        returns the first block number.
    """

    try:
        with Database() as db:
            db.execute(
                """
                SELECT block_number
                FROM ?
                ORDER BY block_number DESC
                LIMIT 1
                """,
                (event_name),
            )
            latest_block = db.fetchone()

            if latest_block:
                log.debug(f"Found the event:{event_name} on database: {latest_block}")
                return latest_block[0]
    except Exception as e:
        raise DatabaseError(f"Error finding latest block for {event_name}") from e

    start: int = int(CONFIG.chains[SDK.network.name].start)
    log.debug(
        f"Could not find the event:{event_name} on database. \
            Proceeding with default initial block:{start}"
    )
    return CONFIG.chains[SDK.network.name].start


def create_alienated_table() -> None:
    """Creates the sql database table for Alienated.

    Raises:
        DatabaseError: Error creating Alienated table
    """

    try:
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
        log.debug(f"Created a new table: Alienated")
    except Exception as e:
        raise DatabaseError("Error creating Alienated table") from e


def create_delegation_table() -> None:
    """Creates the sql database table for Delegation.

    Raises:
        DatabaseError: Error creating Delegation table
    """

    try:
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
                    FOREIGN KEY (pool_id) REFERENCES Pools (id),
                    PRIMARY KEY (pool_id, operator_id)
                )
                """
            )
        log.debug(f"Created a new table: Delegation")
    except Exception as e:
        raise DatabaseError("Error creating Delegation table") from e


def create_deposit_table() -> None:
    """Creates the sql database table for Deposit.

    Raises:
        DatabaseError: Error creating Deposit table
    """

    try:
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
                    FOREIGN KEY (pool_id) REFERENCES Pools (id),
                    PRIMARY KEY (pool_id)
                )
                """
            )
        log.debug(f"Created a new table: Deposit")
    except Exception as e:
        raise DatabaseError("Error creating Deposit table") from e


def create_fallback_operator_table() -> None:
    """Creates the sql database table for FallbackOperator.

    Raises:
        DatabaseError: Error creating FallbackOperator table
    """

    try:
        with Database() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS FallbackOperator (
                    pool_id TEXT NOT NULL,
                    fallback_threshold INTEGER NOT NULL,
                    block_number INTEGER NOT NULL,
                    transaction_index INTEGER NOT NULL,
                    log_index INTEGER NOT NULL,
                    FOREIGN KEY (pool_id) REFERENCES Pools (id),
                    PRIMARY KEY (pool_id)
                )
                """
            )
        log.debug(f"Created a new table: FallbackOperator")
    except Exception as e:
        raise DatabaseError("Error creating FallbackOperator table") from e


def create_id_initiated_table() -> None:
    """Creates the sql database table for IdInitiated.

    Raises:
        DatabaseError: Error creating IdInitiated table
    """

    try:
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
        log.debug(f"Created a new table: IdInitiated")
    except Exception as e:
        raise DatabaseError("Error creating IdInitiated table") from e


def create_exit_request_table() -> None:
    """Creates the sql database table for ExitRequest.

    Raises:
        DatabaseError: Error creating ExitRequest table
    """

    try:
        with Database() as db:
            db.execute(
                """
                 CREATE TABLE IF NOT EXISTS ExitRequest (
                     pk TEXT NOT NULL,
                     block_number INTEGER NOT NULL,
                     transaction_index INTEGER NOT NULL,
                     log_index INTEGER NOT NULL,
                     FOREIGN KEY (pk) REFERENCES validators(pk),
                     PRIMARY KEY (pk)
                 )
                """
            )
        log.debug(f"Created a new table: ExitRequest")
    except Exception as e:
        raise DatabaseError("Error creating ExitRequest table") from e


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

    Returns:
        Iterable[EventData]: list of events.
    """
    if filter_func is not None:
        events: Iterable[EventData] = filter(filter_func, events)
    saveable_events: list[tuple] = parser(events)
    saver(saveable_events)

    return events
