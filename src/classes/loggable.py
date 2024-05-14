# -*- coding: utf-8 -*-
import os
import logging
from logging import StreamHandler, Formatter
from logging.handlers import TimedRotatingFileHandler
from typing import Any
from src.globals import CONFIG


class Loggable:
    """A helper class to make logging easier for other classes. It initializes a logger object with given streams and files.
    It uses the configuration file to set the log level, log directory, log file name, log file rotation interval, etc.

    Example:
        class MyClass(Loggable):
            def __init__(self):
                Loggable.__init__(self, name="MY_CLASS")
                self.logger.info("This is an info message.")
                self.logger.error("This is an error message.")

    Attributes:
        __logger_name (str): Unique name for the logger, log file and object instance using given streams, max 25 char.
        logger (obj): Logger object to be used in the class.

    Raises:
        ValueError: Name length should be max 25 characters.
    """

    def __init__(self, name: str) -> None:
        """Initializes a Loggable object.

        Args:
            name (str): Unique name for the logger, log file and object instance using given streams, max 25 char.

        Raises:
            ValueError: Name length should be max 25 characters.
        """
        __name_len = 25
        if len(name) > __name_len:
            raise ValueError(f"Name length should be max {__name_len} characters.")
        # TODO: what is < doing before __name_len?
        self.__logger_name: str = f"{name:<__name_len}"

        self.logger: logging.Logger = self.__get_logger(name)

    def __get_logger(self, name: str) -> logging.Logger:
        """Initializes and returns a logger object with given streams and files.

        Args:
            name (str): Unique name for the logger, log file and object instance using given streams, max 25 char.

        Returns:
            logging.Logger: Logger object to be used in the class.
        """

        logger: logging.Logger = logging.getLogger(name=name)
        logging.basicConfig()
        logger.propagate = False

        if CONFIG.logger.stream:
            logger.addHandler(self.__get_stream_handler())

        if CONFIG.logger.file:
            logger.addHandler(self.__get_file_handler(name=name))

        return logger

    @property
    def __level(self) -> Any:
        """Returns the logger level: DEBUG, INFO, WARNING, ERROR, CRITICAL.

        Returns:
            Any: Logger level name
        """

        # returns the level name as a string or an integer
        return logging.getLevelName(CONFIG.logger.level)

    @property
    def __file_formatter(self) -> Formatter:
        """Returns the logger formatter for file as a property.

        Example formatted msg for BLOCK_DAEMON file:
            [09:28:05] CRITICAL :: critical message

        Returns:
            Formatter: Formatter object to be used in the logger.
        """

        return Formatter(
            fmt=f"[%(asctime)s] %(levelname)-8s :: %(message)s",
            datefmt="%H:%M:%S",
        )

    @property
    def __stream_formatter(self) -> Formatter:
        """Returns the logger formatter for stream as a property.

        Example formatted msg for stream:
            [09:28:05] BLOCK_DAEMON | CRITICAL ::critical message

        Returns:
            Formatter: Formatter object to be used in the logger.
        """

        return Formatter(
            fmt=f"[%(asctime)s] {self.__logger_name} | %(levelname)-8s :: %(message)s",
            datefmt="%H:%M:%S",
        )

    def __get_stream_handler(self) -> StreamHandler:
        """Returns an initialized Stream Handler.

        Returns:
            StreamHandler: Initialized and Configured Stream Handler
        """

        sh: StreamHandler = StreamHandler()
        sh.setFormatter(self.__stream_formatter)
        sh.setLevel(self.__level)
        return sh

    def __get_file_handler(self, name: str) -> TimedRotatingFileHandler:
        """Returns an initialized File Handler.

        Args:
            name (str): Name of the log file to be created.

        Returns:
            TimedRotatingFileHandler: Initialized and Configured File Handler
        """

        main_dir: str = CONFIG.directory
        log_dir: str = CONFIG.logger.directory
        path: str = os.path.join(main_dir, log_dir, name)
        if not os.path.exists(path):
            os.makedirs(path)
        fh: TimedRotatingFileHandler = TimedRotatingFileHandler(
            os.path.join(path, "log"),
            when=CONFIG.logger.when,
            interval=CONFIG.logger.interval,
            backupCount=CONFIG.logger.backup,
        )
        fh.suffix = "%Y-%m-%d"

        fh.setFormatter(self.__file_formatter)
        fh.setLevel(self.__level)
        return fh
