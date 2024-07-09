# -*- coding: utf-8 -*-

from .config import CONFIG
from .sdk import SDK

network: str = SDK.network.name
chain: dict = CONFIG.chains[network]

one_minute: int = 60
one_hour: int = 60 * one_minute
hour_blocks: int = one_hour // int(chain.interval)
