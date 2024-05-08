# -*- coding: utf-8 -*-

from typing import List
from src.classes import Daemon, Trigger


class TimeDaemon(Daemon):
    """A Daemon that triggers provided actions on every X seconds. Task returns True, simply run.

    Example:
        def action():
            print(datetime.datetime.now())

        t = Trigger(action)
        b = TimeDaemon(triggers=[t])

    Attributes:
        name (str): name of the daemon to be used when logging etc. (value: TIME_DAEMON)
    """

    name: str = "TIME_DAEMON"

    def __init__(self, interval: int, triggers: List[Trigger]) -> None:
        Daemon.__init__(
            self,
            name=self.name,
            interval=interval,
            task=self.trigger,
            triggers=triggers,
        )

    def trigger(self) -> bool:
        """Returns true and triggers the action.

        Returns:
            bool: True
        """
        return True
