# -*- coding: utf-8 -*-

from src.classes import Database
from src.globals import OPERATOR_ID
from src.logger import log
from src.exceptions import DatabaseError


def create_operators_table() -> None:
    """Creates the Operators table in the database.

    Raises:
        DatabaseError: Error creating table Operators
    """
    log.debug("Creating Operators table.")
    try:
        with Database() as db:
            db.execute(
                f"""
                CREATE TABLE IF NOT EXISTS Operators (
                    id INTEGER PRIMARY KEY DEFAULT {OPERATOR_ID},
                    last_stake_ts TIMESTAMP DEFAULT 0
                )
                """
            )
    except Exception as e:
        raise DatabaseError("Error creating table Operators") from e


def drop_operators_table() -> None:
    """Drops the Operators table from the database.

    Raises:
        DatabaseError: Error dropping table Operators
    """
    log.debug("Dropping Operators table.")
    try:
        with Database() as db:
            db.execute("DROP TABLE IF EXISTS Operators")
    except Exception as e:
        raise DatabaseError("Error dropping table Operators") from e


def reinitialize_operators_table() -> None:
    """Drops and recreates the Operators table in the database."""
    log.debug("Reinitializing Operators table.")
    drop_operators_table()
    create_operators_table()


def save_last_stake_timestamp(timestamp: int) -> None:
    """Saves the last stake timestamp in the Operators table.

    Args:
        timestamp (int): The timestamp to save in the table
    """
    log.debug(f"Saving last stake timestamp: {timestamp}")
    try:
        with Database() as db:
            db.execute(
                """
                UPDATE Operators
                SET last_stake_ts = ?
                WHERE id = ?
                """,
                (timestamp, OPERATOR_ID),
            )
    except Exception as e:
        raise DatabaseError("Error saving last stake timestamp") from e
