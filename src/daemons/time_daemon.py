# -*- coding: utf-8 -*-

from typing_extensions import Self
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

    def __init__(self, interval: int, triggers: list[Trigger], initial_delay: int) -> None:
        Daemon.__init__(
            self,
            name=self.name,
            interval=interval,
            task=self.trigger,
            triggers=triggers,
            initial_delay=initial_delay,
        )

    def trigger(self) -> Self:
        """Returns self. Self will be used to stop the deamon when needed by trigger itself
        since return value will be passed to the trigger function.

        Returns:
            Self: self
        """
        return self
