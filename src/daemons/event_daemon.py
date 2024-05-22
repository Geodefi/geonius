# -*- coding: utf-8 -*-

from typing import Iterable
from web3.types import EventData
from web3.contract.contract import ContractEvent
from src.classes import Daemon, Trigger
from src.globals import SDK, chain

from src.logger import log
from src.helpers import get_all_events
from src.utils import send_email


class EventDaemon(Daemon):
    """A type of Block Daemon that triggers every time the provided event is emitted.
    Interval is default block time (12s)
    Task returns the events as a list. If no events are emitted, returns None.

    Attributes:
        __recent_block (int): recent block number to be processed.
        name (str): name of the daemon to be used when logging etc. (value: EVENT_DAEMON)
        event (_type_): event to be checked.
        block_period (int): number of blocks to wait before running the triggers.
        block_identifier (int): block_identifier sets if we are looking for 'latest', 'earliest', 'pending', 'safe', 'finalized'.
    """

    name: str = "EVENT_DAEMON"

    def __init__(
        self,
        trigger: Trigger,
        event: ContractEvent,
        start_block: int = chain.start,
    ) -> None:
        """Initializes a EventDaemon object. The daemon will run the trigger on every event emitted.

        Args:
            trigger (Trigger): an initialized Trigger instance.
            event (ContractEvent): event to be checked.
            start_block (int, optional): block number to start checking for events. Default is what is set in the config.
        """

        Daemon.__init__(
            self,
            interval=int(chain.interval) + 1,
            task=self.listen_events,
            trigger=trigger,
        )
        self.event = event

        # block_identifier sets if we are looking for:
        # 'latest', 'earliest', 'pending', 'safe', 'finalized'.
        self.block_identifier: str = chain.identifier
        self.block_period: int = int(chain.period)
        self.__recent_block: int = start_block
        log.debug(f"{trigger.name} is attached to an Event Daemon")

    def listen_events(self) -> Iterable[EventData]:
        """The main task for the EventDaemon. Checks for new events. If any, runs the trigger and returns the events.
        If no events are emitted, returns None.

        Returns:
            list[dict]: list of events as dictionaries.
        """

        # eth.block_number or eth.get_block_number() can also be used
        # but this allows block_identifier.
        curr_block: int = (SDK.w3.eth.get_block(self.block_identifier)).number
        log.debug(f"New block detected: {curr_block}")

        # check if required number of blocks have past:
        if curr_block > self.__recent_block + self.block_period:
            try:
                events = get_all_events(
                    event=self.event,
                    first_block=self.__recent_block,
                    last_block=curr_block,
                )
            except Exception as e:
                log.error(e)
                send_email(e.__class__.__name__, str(e), [("<file_path>", "<file_name>.log")])
                events = []

            # save events to db
            if events:
                log.debug(f"{self.trigger.name} will be triggered")
                self.__recent_block = curr_block
                return events
            else:
                return None
        else:
            log.debug(
                f"Block period have not been met yet.\
                Expected block:{self.__recent_block + self.block_period}"
            )
            return None
