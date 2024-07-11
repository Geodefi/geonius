# -*- coding: utf-8 -*-

import os
from typing import Any
import logging
from logging import StreamHandler, Formatter
from logging.handlers import TimedRotatingFileHandler

from src.globals import get_config


class Loggable:
    """
    A class to create a logger object with given streams and files. Supposed to be used as a
    global var. Logger functions can also be directly reached.

    Example:
        logger = Loggable()
        logger.info("info message")
        logger.error("error message")

        OR

        from src.global.logger import log
        log.info("info message")
        log.error("error message")


    Attributes:
        logger (obj): Logger object to be used in the class.

    """

    def __init__(self) -> None:
        """Initializes a Loggable object."""
        logger: logging.Logger = self.__get_logger()
        logger.info("Initalized a global logger.")
        self.logger = logger

    def __get_logger(self) -> logging.Logger:
        """Initializes and returns a logger object with given streams and files.

        Returns:
            logging.Logger: Logger object to be used in the class.
        """

        logger: logging.Logger = logging.getLogger()
        logger.setLevel(self.__level)
        logger.propagate = False

        handlers: list = list()
        if get_config().logger.stream:
            stream_handler: StreamHandler = self.__get_stream_handler()
            handlers.append(stream_handler)
            logger.addHandler(stream_handler)
            logger.info(f"Logger is provided with a stream handler. Level: {self.__level}")

        if get_config().logger.file:
            file_handler: TimedRotatingFileHandler = self.__get_file_handler()
            handlers.append(file_handler)
            logger.addHandler(file_handler)
            logger.info(f"Logger is provided with a file handler. Level: {self.__level}")

        logging.basicConfig(handlers=handlers, force=True)
        return logger

    @property
    def __level(self) -> str:
        """Returns the logger level from user configuration.

        Returns:
            str: Logger level name
        """
        return get_config().logger.level

    @property
    def __formatter(self) -> Formatter:
        """Returns the logger formatter with Multithread support.

        Example formatted msg for stream:
            [01:35:56] STAKE                | INFO     :: 0 new verified public keys are detected.

        Returns:
            Formatter: Formatter object to be used in the logger.
        """

        return Formatter(
            fmt=f"[%(asctime)s] %(threadName)-29s | %(levelname)-8s :: %(message)s",
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

        main_dir: str = get_config().directory
        log_dir: str = get_config().logger.directory
        path: str = os.path.join(main_dir, log_dir)
        if not os.path.exists(path):
            os.makedirs(path)
        prefix: str = "log"
        filename: str = os.path.join(path, prefix)
        fh: TimedRotatingFileHandler = TimedRotatingFileHandler(
            filename,
            when=get_config().logger.when,
            interval=get_config().logger.interval,
            backupCount=get_config().logger.backup,
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

    def etherscan(self, function_name: str, tx_hash: str) -> None:
        self.logger.info(
            f"{function_name} tx sent: https://holesky.etherscan.io/tx/{tx_hash.hex()}"
        )  # TODO: this needs to change for mainnet
