# -*- coding: utf-8 -*-

# assuming avg 1 hour  == 300 blocks
hour_blocks: int = 300

# assuming avg  1 block == 12 sec
block_seconds: int = 12

# number of blocks to divide the given range into multiple ranges while searching for events
MAX_BLOCK_RANGE: int = 3_000  # TODO: might be given as a flag param
