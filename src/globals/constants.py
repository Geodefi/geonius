# -*- coding: utf-8 -*-

from .config import CONFIG
from .sdk import SDK

network: str = SDK.network.name
chain: dict = CONFIG.chains[network]
hour_blocks: int = 3600 // int(chain.interval)
