# -*- coding: utf-8 -*-

from threading import Lock

from src.classes.database import Database
from src.common import AttributeDict
from src.exceptions import DatabaseError
from src.globals import get_logger, get_constants

alienated_mutex = Lock()
delegation_mutex = Lock()
deposit_mutex = Lock()
fallback_mutex = Lock()
id_initiated_mutex = Lock()
exit_request_mutex = Lock()


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
                get_logger().debug(f"Found on database:{event_name} => {e[0]}/{e[1]}/{e[2]}")
                return AttributeDict.convert_recursive(
                    {"block_number": e[0], "transaction_index": e[1], "log_index": e[2]}
                )

    except Exception as e:
        raise DatabaseError(f"Error finding latest block for {event_name}") from e

    init_block = int(get_constants().chain.start)
    get_logger().debug(
        f"Could not find the event:{event_name} on database. \
            Proceeding with default initial block:{init_block}"
    )
    return AttributeDict.convert_recursive(
        {"block_number": init_block, "transaction_index": 0, "log_index": 0}
    )


def create_alienated_table() -> None:
    """Creates the sql database table for Alienated.

    Raises:
        DatabaseError: Error creating Alienated table
    """

    with alienated_mutex:
        try:
            with Database() as db:
                db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS Alienated (
                        pk TEXT NOT NULL,
                        block_number INTEGER NOT NULL,
                        transaction_index INTEGER NOT NULL,
                        log_index INTEGER NOT NULL,
                        FOREIGN KEY (pk) REFERENCES Validators (pk)
                    )
                    """
                )
            get_logger().debug(f"Created a new table: Alienated")
        except Exception as e:
            raise DatabaseError("Error creating Alienated table") from e


def drop_alienated_table() -> None:
    """Removes Alienated table from the database.

    Raises:
        DatabaseError: Error dropping Alienated table
    """

    try:
        with Database() as db:
            db.execute("""DROP TABLE IF EXISTS Alienated""")
        get_logger().debug(f"Dropped Table: Alienated")
    except Exception as e:
        raise DatabaseError(f"Error dropping Alienated table") from e


def reinitialize_alienated_table() -> None:
    """Removes Alienated table and creates an empty one."""

    drop_alienated_table()
    create_alienated_table()


def create_delegation_table() -> None:
    """Creates the sql database table for Delegation.

    Raises:
        DatabaseError: Error creating Delegation table
    """
    with delegation_mutex:
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
                        FOREIGN KEY (pool_id) REFERENCES Pools (id)
                    )
                    """
                )
            get_logger().debug(f"Created a new table: Delegation")
        except Exception as e:
            raise DatabaseError("Error creating Delegation table") from e


def drop_delegation_table() -> None:
    """Removes Delegation table from the database.

    Raises:
        DatabaseError: Error dropping Delegation table
    """
    with deposit_mutex:
        try:
            with Database() as db:
                db.execute("""DROP TABLE IF EXISTS Delegation""")
            get_logger().debug(f"Dropped Table: Delegation")
        except Exception as e:
            raise DatabaseError(f"Error dropping Delegation table") from e


def reinitialize_delegation_table() -> None:
    """Removes delegation table and creates an empty one."""

    drop_delegation_table()
    create_delegation_table()


def create_deposit_table() -> None:
    """Creates the sql database table for Deposit.

    Raises:
        DatabaseError: Error creating Deposit table
    """
    with deposit_mutex:
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
                        FOREIGN KEY (pool_id) REFERENCES Pools (id)
                    )
                    """
                )
            get_logger().debug(f"Created a new table: Deposit")
        except Exception as e:
            raise DatabaseError("Error creating Deposit table") from e


def drop_deposit_table() -> None:
    """Removes Deposit table from the database.

    Raises:
        DatabaseError: Error dropping deposit table
    """

    try:
        with Database() as db:
            db.execute("""DROP TABLE IF EXISTS Deposit""")
        get_logger().debug(f"Dropped Table: Deposit")
    except Exception as e:
        raise DatabaseError(f"Error dropping Deposit table") from e


def reinitialize_deposit_table() -> None:
    """Removes deposit table and creates an empty one."""

    drop_deposit_table()
    create_deposit_table()


def create_fallback_operator_table() -> None:
    """Creates the sql database table for FallbackOperator.

    Raises:
        DatabaseError: Error creating FallbackOperator table
    """
    with fallback_mutex:
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
                        FOREIGN KEY (pool_id) REFERENCES Pools (id)
                    )
                    """
                )
            get_logger().debug(f"Created a new table: FallbackOperator")
        except Exception as e:
            raise DatabaseError("Error creating FallbackOperator table") from e


def drop_fallback_operator_table() -> None:
    """Removes FallbackOperator table from the database.

    Raises:
        DatabaseError: Error dropping FallbackOperator table
    """

    try:
        with Database() as db:
            db.execute("""DROP TABLE IF EXISTS FallbackOperator""")
        get_logger().debug(f"Dropped Table: FallbackOperator")
    except Exception as e:
        raise DatabaseError(f"Error dropping FallbackOperator table") from e


def reinitialize_fallback_operator_table() -> None:
    """Removes FallbackOperator table and creates an empty one."""

    drop_fallback_operator_table()
    create_fallback_operator_table()


def create_id_initiated_table() -> None:
    """Creates the sql database table for IdInitiated.

    Raises:
        DatabaseError: Error creating IdInitiated table
    """
    with id_initiated_mutex:
        try:
            with Database() as db:
                db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS IdInitiated (
                        pool_id TEXT UNIQUE NOT NULL,
                        block_number INTEGER NOT NULL,
                        transaction_index INTEGER NOT NULL,
                        log_index INTEGER NOT NULL,
                        FOREIGN KEY (pool_id) REFERENCES Pools (id)
                    )
                    """
                )
            get_logger().debug(f"Created a new table: IdInitiated")
        except Exception as e:
            raise DatabaseError("Error creating IdInitiated table") from e


def drop_id_initiated_table() -> None:
    """Removes IdInitiated table from the database.

    Raises:
        DatabaseError: Error dropping IdInitiated table
    """

    try:
        with Database() as db:
            db.execute("""DROP TABLE IF EXISTS IdInitiated""")
        get_logger().debug(f"Dropped Table: IdInitiated")
    except Exception as e:
        raise DatabaseError(f"Error dropping IdInitiated table") from e


def reinitialize_id_initiated_table() -> None:
    """Removes IdInitiated table and creates an empty one."""

    drop_id_initiated_table()
    create_id_initiated_table()


def create_exit_request_table() -> None:
    """Creates the sql database table for ExitRequest.

    Raises:
        DatabaseError: Error creating ExitRequest table
    """
    with exit_request_mutex:
        try:
            with Database() as db:
                db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS ExitRequest (
                        pk TEXT UNIQUE NOT NULL,
                        block_number INTEGER NOT NULL,
                        transaction_index INTEGER NOT NULL,
                        log_index INTEGER NOT NULL,
                        FOREIGN KEY (pk) REFERENCES Validators (pk),
                        PRIMARY KEY (pk)
                    )
                    """
                )
            get_logger().debug(f"Created a new table: ExitRequest")
        except Exception as e:
            raise DatabaseError("Error creating ExitRequest table") from e


def drop_exit_request_table() -> None:
    """Removes ExitRequest table from the database.

    Raises:
        DatabaseError: Error dropping ExitRequest table
    """

    try:
        with Database() as db:
            db.execute("""DROP TABLE IF EXISTS ExitRequest""")
        get_logger().debug(f"Dropped Table: ExitRequest")
    except Exception as e:
        raise DatabaseError(f"Error dropping ExitRequest table") from e


def reinitialize_exit_request_table() -> None:
    """Removes ExitRequest table and creates an empty one."""

    drop_exit_request_table()
    create_exit_request_table()
