# -*- coding: utf-8 -*-

import os
from typing import Any
import logging
from logging import StreamHandler, Formatter
from logging.handlers import TimedRotatingFileHandler
from src.globals import CONFIG


class Loggable:
    """A helper class to make logging easier for other classes. It initializes a logger object with given streams and files.
    It uses the configuration file to set the log level, log directory, log file name, log file rotation interval, etc.

    Example:
        class MyClass(Loggable):
            def __init__(self):
                Loggable.__init__(self)
                self.logger.info("This is an info message.")
                self.logger.error("This is an error message.")

    Attributes:
        logger (obj): Logger object to be used in the class.

    """

    def __init__(self) -> None:
        """Initializes a Loggable object."""

        self.logger: logging.Logger = self.__get_logger()

    def __get_logger(self) -> logging.Logger:
        """Initializes and returns a logger object with given streams and files.

        Returns:
            logging.Logger: Logger object to be used in the class.
        """
        logging.basicConfig(level=self.__level)

        logger: logging.Logger = logging.getLogger()
        logger.setLevel(self.__level)
        logger.propagate = False

        if CONFIG.logger.stream:
            logger.addHandler(self.__get_stream_handler())

        if CONFIG.logger.file:
            logger.addHandler(self.__get_file_handler())

        return logger

    @property
    def __level(self) -> str:
        """Returns the logger level from user configuration.

        Returns:
            str: Logger level name
        """
        return CONFIG.logger.level

    @property
    def __formatter(self) -> Formatter:
        """Returns the logger formatter with Multithread support.

        Example formatted msg for stream:
            [09:28:05] BLOCK_DAEMON | CRITICAL ::critical message

        Returns:
            Formatter: Formatter object to be used in the logger.
        """

        return Formatter(
            fmt=f"[%(asctime)s] {'%(threadName)s':<25} | %(levelname)-8s :: %(message)s",
            datefmt="%H:%M:%S",
        )

    def __get_stream_handler(self) -> StreamHandler:
        """Returns an initialized Stream Handler.

        Returns:
            StreamHandler: Initialized and Configured Stream Handler
        """

        sh: StreamHandler = StreamHandler()
        sh.setFormatter(self.__formatter)
        sh.setLevel(self.__level)
        return sh

    def __get_file_handler(self) -> TimedRotatingFileHandler:
        """Returns an initialized File Handler.

        Returns:
            TimedRotatingFileHandler: Initialized and Configured File Handler
        """

        main_dir: str = CONFIG.directory
        log_dir: str = CONFIG.logger.directory
        path: str = os.path.join(main_dir, log_dir)
        if not os.path.exists(path):
            os.makedirs(path)
        print(CONFIG.logger)
        prefix: str = "log"
        filename: str = os.path.join(path, prefix)
        fh: TimedRotatingFileHandler = TimedRotatingFileHandler(
            filename,
            when=CONFIG.logger.when,
            interval=CONFIG.logger.interval,
            backupCount=CONFIG.logger.backup,
        )

        fh.setFormatter(self.__formatter)
        fh.setLevel(self.__level)
        return fh

    def __getattr__(self, attr: str) -> Any:
        """Added so, `self.info()` can be used instead of `self.logger.<log_level>()`

        Args:
            attr (str): Attribute to be get.

        Returns:
            Any: Attribute of the object.
        """

        return getattr(self.logger, attr)
