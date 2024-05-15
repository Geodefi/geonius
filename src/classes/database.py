# -*- coding: utf-8 -*-
import os
import sqlite3 as sql
from typing import Any
from src.globals import CONFIG


class Database:
    """A helper class makes database management easier for other classes..

    Example:
        with Database() as db:
            db.execute(
                '''CREATE TABLE IF NOT EXISTS {db_name} (
                    column_name TEXT NOT NULL
                )
            ''')

    Attributes:
        main_dir (str): Main directory of the project.
        db_dir (str): Directory to store the database files.
        db_name (str): Name of the database file.
        db_ext (str): Extension of the database file.
        path (str): Path of the database file.
        connection (sqlite3.Connection): Connection object to the database file.
        cursor (sqlite3.Cursor): Cursor object to the database file.
    """

    main_dir: str = CONFIG.directory
    db_dir: str = CONFIG.database.directory
    db_name: str = "operator"
    db_ext: str = ".db"

    def __init__(self, db_name: str = db_name) -> None:
        """Initializes a Database object.

        Args:
            db_name (str, optional): Name of the database file. Defaults to `operator`.
        """

        self.db_name: str = db_name
        self.path: str = os.path.join(self.main_dir, self.db_dir)
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        try:
            # log(sql.version) #pyselite version
            # log(sql.sqlite_version) #SQLLite engine version
            self.connection: sql.Connection = sql.connect(
                os.path.join(self.path, self.db_name + self.db_ext)
            )
            self.cursor: sql.Cursor = self.connection.cursor()
        except Exception as e:
            raise e

    def __enter__(self):
        """Used when entering a `with` statement. Which is safer when using database."""

        return self

    def __exit__(self, ext_type, exc_value, traceback) -> None:
        """Used when exiting from a `with` statement.
        Disconnects from the Database file and closes.

        Args:
            ext_type (Type): Type of the exception.
            exc_value (Exception): Exception object.
            traceback (Traceback): Traceback object.
        """

        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()

    def __getattr__(self, attr: str) -> Any:
        """Added so, `self.execute()` can be used instead of `self.cursor.execute()`

        Args:
            attr (str): Attribute to be get.

        Returns:
            Any: Attribute of the object.
        """

        return getattr(self.cursor, attr)
