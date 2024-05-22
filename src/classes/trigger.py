# -*- coding: utf-8 -*-

from typing import Callable
from src.logger import log


class Trigger:
    """Bound to a Daemon, a Trigger also processes the changes of the daemon after a loop.
    A trigger can only have 1 action. It is a callable object. It is used to process the changes of the daemon.

    Example:
        def action():
            print(datetime.datetime.now())

        t = Trigger(action)

    Attributes:
        __action (Callable): Function to be called when Triggered.
    """

    def __init__(self, name: str, action: Callable) -> None:
        """Initializes a Trigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.

        Args:
            name (str): name of the trigger to be used when logging etc. Every Trigger must have a name. 5-25 char.
            action (Callable): function to be called when Triggered.

        Raises:
            ValueError: Name length should be max 25 characters.
        """

        __name_len = 25
        if len(name) > __name_len:
            raise ValueError(f"Name length should be max {__name_len} characters.")
        self.name: str = name

        log.info(f"Trigger {name} is initalized.")
        self.__register_action(action)

    def __register_action(self, action: Callable) -> None:
        """Registers the action to be called during the processing of the daemon's changes.

        Args:
            action (Callable): function to be called when Triggered.
        """

        self.__action: Callable = action

    def process(self, *args, **kwargs) -> None:
        """Processes the changes of the daemon after a loop.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """

        self.__action(*args, **kwargs)
