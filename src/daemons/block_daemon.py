# -*- coding: utf-8 -*-

# TODO: search for 'from ..' and use module import with src.
from src.classes import Daemon, Trigger
from src.globals import SDK, CONFIG, block_seconds


class BlockDaemon(Daemon):
    """
    A Daemon that triggers provided actions on every X block on the blockchain.
    Interval is default block time (12s).
    Task returns: last block number which activates the triggers.
    ...

    Attributes:
        name (str): block_daemon
        last_block (int): latest block that is checked.
    """

    name: str = "BLOCK_DAEMON"

    def __init__(self, triggers: list[Trigger]):
        """Initializes the configured daemon.
        Args:
            triggers (list): List of initialized Trigger instances
            event (str): event to be checked.
        """
        Daemon.__init__(
            self,
            name=self.name,
            interval=block_seconds,
            task=self.listen_blocks,
            triggers=triggers,
        )

        # block_identifier sets if we are looking for 'latest', 'earliest', 'pending', 'safe', 'finalized'.
        self.block_identifier: int = CONFIG.chains[SDK.network.name].identifier
        self.block_period: int = int(CONFIG.chains[SDK.network.name].period)

        self.__recent_block: int = CONFIG.chains[SDK.network.name].first_block

    def listen_blocks(self) -> int:
        """The main task for the BlockDaemon.
        1. Checks for new blocks.
        2. On every X block (period by config), runs the triggers.

        Returns:
            int : latest block.
        """
        # eth.block_number or eth.get_block_number() can also be used
        # but this allows block_identifier.
        curr_block = SDK.w3.eth.get_block(self.block_identifier)

        # check if required number of blocks have past:
        if curr_block.number > self.__recent_block + self.block_period:
            #   returns the latest block number
            self.__recent_block = curr_block.number
            return curr_block
        else:
            return None
