# -*- coding: utf-8 -*-

from src.classes.database import Database
from src.globals import get_logger, get_env
from src.exceptions import DatabaseError


def create_operators_table() -> None:
    """Creates the Operators table in the database.

    Raises:
        DatabaseError: Error creating table Operators
    """
    get_logger().debug("Creating Operators table.")
    try:
        with Database() as db:
            db.execute(
                f"""
                CREATE TABLE IF NOT EXISTS Operators (
                    id TEXT PRIMARY KEY,
                    last_stake_ts INTEGER
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
    get_logger().debug("Dropping Operators table.")
    try:
        with Database() as db:
            db.execute("DROP TABLE IF EXISTS Operators")
    except Exception as e:
        raise DatabaseError("Error dropping table Operators") from e


def reinitialize_operators_table() -> None:
    """Drops and recreates the Operators table in the database."""
    get_logger().debug("Reinitializing Operators table.")
    drop_operators_table()
    create_operators_table()
    with Database() as db:
        db.executemany(
            "INSERT INTO Operators VALUES (?,?)",
            [
                (
                    str(get_env().OPERATOR_ID),
                    0,
                ),
            ],
        )


def save_last_stake_timestamp(timestamp: int) -> None:
    """Saves the last stake timestamp in the Operators table.

    Args:
        timestamp (int): The timestamp to save in the table
    """
    get_logger().debug(f"Saving last stake timestamp: {timestamp}")
    try:
        with Database() as db:
            db.execute(
                """
                UPDATE Operators
                SET last_stake_ts = ?
                WHERE id = ?
                """,
                (timestamp, get_env().OPERATOR_ID),
            )
    except Exception as e:
        raise DatabaseError("Error saving last stake timestamp") from e
