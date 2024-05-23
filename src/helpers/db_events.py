# -*- coding: utf-8 -*-

from typing import Callable, Iterable
from web3.types import EventData

from src.classes import Database
from src.globals import chain
from src.logger import log
from src.exceptions import DatabaseError
from src.utils import AttributeDict, convert_recursive


def find_latest_event(event_name: str) -> AttributeDict:
    """Finds the latest eventt info for the given event_name in the database.

    Args:
        event_name (str): Name of the event.

    Returns:
        AttributeDict: Blocknumber, tx index and log index \
            that will define the starting point for the given event_name. \
                If no event is found in database, returns provided default start info.
    """

    try:
        with Database() as db:
            db.execute(
                f"""
                SELECT block_number,transaction_index,log_index
                FROM {event_name}
                ORDER BY block_number DESC, transaction_index DESC, log_index DESC
                LIMIT 1
                """,
            )
            found_event = db.fetchone()
            if found_event:
                e = found_event
                log.debug(f"Found on database:{event_name} => {e[0]}/{e[1]}/{e[2]}")
                return convert_recursive(
                    {"block_number": e[0], "transaction_index": e[1], "log_index": e[2]}
                )

    except Exception as e:
        raise DatabaseError(f"Error finding latest block for {event_name}") from e

    log.debug(
        f"Could not find the event:{event_name} on database. \
            Proceeding with default initial block:{chain.start}"
    )
    return convert_recursive(
        {"block_number": int(chain.start), "transaction_index": 0, "log_index": 0}
    )


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
    if filter_func:
        events: Iterable[EventData] = list(filter(filter_func, events))
    saveable_events: list[tuple] = parser(events)
    saver(saveable_events)

    return events
