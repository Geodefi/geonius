# -*- coding: utf-8 -*-

from src.classes import Daemon, Trigger


class TimeDaemon(Daemon):
    """Simplest Daemon that triggers an action every X second auto.
    Task returns "True (boolean)". Simply, run.
    """

    name: str = "TIME_DAEMON"

    def __init__(self, interval: int, triggers: list[Trigger]):
        Daemon.__init__(
            self,
            name=self.name,
            interval=interval,
            task=self.trigger,
            triggers=triggers,
        )

    def trigger(self) -> dict:
        """Returns true and triggers the action."""
        return True
