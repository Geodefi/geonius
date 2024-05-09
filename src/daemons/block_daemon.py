# -*- coding: utf-8 -*-

from src.classes import Daemon, Trigger
from src.globals import SDK, CONFIG


class BlockDaemon(Daemon):
    """A Daemon that triggers provided actions on every X block on the blockchain.
    Interval is default block time (12s).
    Task returns: last block number which activates the triggers.

    Example:
        def action():
            print(datetime.datetime.now())

        t = Trigger(action)
        b = BlockDaemon(triggers=[t])

    Attributes:
        __recent_block (int): recent block number to be processed.
        name (str): name of the daemon to be used when logging etc. (value: BLOCK_DAEMON)
        block_period (int): number of blocks to wait before running the triggers.
        block_identifier (int): block_identifier sets if we are looking for 'latest', 'earliest', 'pending', 'safe', 'finalized'.
    """

    name: str = "BLOCK_DAEMON"

    def __init__(
        self,
        triggers: list[Trigger],
        block_period: int = int(CONFIG.chains[SDK.network.name].period),
    ) -> None:
        """Initializes a BlockDaemon object. The daemon will run the triggers on every X block.

        Args:
            triggers (list[Trigger]): list of initialized Trigger instances.
            block_period (int, optional): number of blocks to wait before running the triggers. Default is what is set in the config.
        """
        Daemon.__init__(
            self,
            name=self.name,
            interval=CONFIG.chains[SDK.network.name].interval,
            task=self.listen_blocks,
            triggers=triggers,
        )

        # block_identifier sets if we are looking for 'latest', 'earliest', 'pending', 'safe', 'finalized'.
        self.block_identifier: int = CONFIG.chains[SDK.network.name].identifier

        self.__recent_block: int = CONFIG.chains[SDK.network.name].start
        self.block_period: int = block_period

    def listen_blocks(self) -> int:
        """The main task for the BlockDaemon.
        1. Checks for new blocks.
        2. On every X block (period by config), runs the triggers. Returns the last block number.

        Returns:
            int: last block number which activates the triggers.
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
