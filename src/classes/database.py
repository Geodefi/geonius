# -*- coding: utf-8 -*-
import os
import sqlite3 as sql
from src.globals import CONFIG


class Database:
    """A helper class makes database management easier for other classes..

    Example:
        with Database() as db:
            db.execute(
                f'''CREATE TABLE IF NOT EXISTS {db_name} (
                    column_name TEXT NOT NULL
                )
            ''')

    Attributes:
        main_dir (str): main directory for geonius folders, provided by config.json.
        db_dir (str): database directory, provided by config.json.
        db_ext (str): database name: operator
        db_ext (str): database extension: .db
    """

    main_dir: str = CONFIG.directory
    db_dir: str = CONFIG.database.directory
    db_name: str = "operator"
    db_ext: str = ".db"

    def __init__(self, db_name: str = db_name):
        """Initializes a Database object.

        Args:
            db_name (int): Optional name of the database
        """

        self.path = os.path.join(self.main_dir, self.db_dir)
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        try:
            # log(sql.version) #pyselite version
            # log(sql.sqlite_version) #SQLLite engine version
            self.connection = sql.connect(
                os.path.join(self.path, db_name + self.db_ext)
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            raise e

    def __enter__(self):
        """Used when entering a `with` statement.
        Which is safer when using database.
        """

        return self

    def __exit__(self, ext_type, exc_value, traceback):
        """Used when exiting from a `with` statement.
        Disconnects from the Database file and closes.
        """

        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()

    def __getattr__(self, attr):
        """Added so, `self.execute()` can be used instead of `self.cursor.execute()`"""

        return getattr(self.cursor, attr)
