# -*- coding: utf-8 -*-

from src.classes import Daemon, Trigger
from src.helpers import get_all_events
from src.globals import SDK, CONFIG, block_seconds


class EventDaemon(Daemon):
    """A type of Block Daemon that triggers every time the provided event is emitted.
    Interval is default block time (12s)
    Task returns the events as a list.
    ...

    Attributes:
        name (str): time_daemon
    """

    name: str = "EVENT_DAEMON"

    def __init__(
        self,
        triggers: list[Trigger],
        event,
        start_block: int = CONFIG.chains[SDK.network.name].first_block,
    ):
        """Initalize an event daemon
        Args:
            triggers (list[Trigger]): List of initialized Trigger instances
            event (_type_): event to be checked.
            start_block (int, optional): Defaults to CONFIG.chains[SDK.network.name].first_block.
        """

        Daemon.__init__(
            self,
            name=self.name,
            interval=block_seconds,
            task=self.listen_events,
            triggers=triggers,
        )

        self.event = event

        # block_identifier sets if we are looking for:
        # 'latest', 'earliest', 'pending', 'safe', 'finalized'.
        self.block_identifier: str = CONFIG.chains[SDK.network.name].identifier
        self.block_period: int = int(CONFIG.chains[SDK.network.name].period)

        self.__recent_block: int = start_block

    def listen_events(self) -> dict:
        """The function that runs every 12 seconds, checks if there are new emits.

        Returns:
            list : sorted list of events emitted since the last check.
        """

        # eth.block_number or eth.get_block_number() can also be used
        # but this allows block_identifier.
        curr_block: int = (SDK.w3.eth.get_block(self.block_identifier)).number

        # check if required number of blocks have past:
        if curr_block > self.__recent_block + self.block_period:
            events = get_all_events(
                event=self.event,
                first_block=self.__recent_block,
                last_block=curr_block,
            )
            # save events to db
            if events:
                self.__recent_block = curr_block
                return events
            else:
                return None
        else:
            return None
