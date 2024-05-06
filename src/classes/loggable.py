# -*- coding: utf-8 -*-
import os
import logging
from logging import StreamHandler, Formatter
from logging.handlers import TimedRotatingFileHandler
from src.globals import CONFIG


class Loggable:
    """
    A helper class to print console statements to a file and/or a stream.

    ...

    Attributes:
        name (str): Unique name of the logger, log file and object instance using given streams.
        logger (:obj:`Logger`): Logger instance to be utilized.

    """

    def __init__(self, name: str):
        """
        Initializes a helper loggable instance.

        Args:
                name (str): Unique name for the logger, max 18 char.
        """

        if len(name) > 18:
            raise Exception

        self.__logger_name: str = f"{name:<18}"
        self.logger: logging.Logger = self.__get_logger(name)

    def __get_logger(self, name: str) -> logging.Logger:
        """Initializes and configures a Logger object.

        Args:
                name (str): Unique name of the logger, log file and object instance using given streams.
        """

        logger = logging.getLogger(name=name)
        logging.basicConfig()
        logger.propagate = False

        # TODO: add flag for --no-log-stream
        logger.addHandler(self.__get_stream_handler())
        # TODO: add flag for --no-log-file
        logger.addHandler(self.__get_file_handler(name=name))

        return logger

    @property
    def __level(self):
        """Returns the logger level: DEBUG, INFO, WARNING, ERROR, CRITICAL"""

        # TODO: add flag for --log-level
        level_name = CONFIG.logger.level
        return logging.getLevelName(level_name)

    @property
    def __file_formatter(self):
        """Returns the logger formatter for file as a property.

        Example formatted msg for BLOCK_DAEMON file:
                [09:28:05] CRITICAL :: critical message
        """

        return Formatter(
            fmt=f"[%(asctime)s] %(levelname)-8s :: %(message)s",
            datefmt="%H:%M:%S",
        )

    @property
    def __stream_formatter(self):
        """Returns the logger formatter for stream as a property.

        Example formatted msg for stream:
                [09:28:05] BLOCK_DAEMON | CRITICAL ::critical message
        """

        return Formatter(
            fmt=f"[%(asctime)s] {self.__logger_name} | %(levelname)-8s :: %(message)s",
            datefmt="%H:%M:%S",
        )

    def __get_stream_handler(self):
        """
        Returns:
                sh (obj): Initialized Stream Handler
        """

        sh = StreamHandler()
        sh.setFormatter(self.__stream_formatter)
        sh.setLevel(self.__level)
        return sh

    def __get_file_handler(self, name: str):
        """
        Returns:
                fh (obj): Initialized and Configured File Handler
                name (str): will be used as a file name.
        """

        main_dir = CONFIG.directory
        log_dir = CONFIG.logger.directory
        path = os.path.join(main_dir, log_dir, name)
        if not os.path.exists(path):
            os.makedirs(path)
        fh = TimedRotatingFileHandler(
            os.path.join(path, "log"),
            when=CONFIG.logger.when,
            interval=CONFIG.logger.interval,
            backupCount=CONFIG.logger.backupCount,
        )
        fh.suffix = "%Y-%m-%d"

        fh.setFormatter(self.__file_formatter)
        fh.setLevel(self.__level)
        return fh
