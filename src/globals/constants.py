# -*- coding: utf-8 -*-
from .config import CONFIG
from .sdk import SDK

hour_blocks: int = 3600 // CONFIG.chains[SDK.network.name].interval


pools_table: str = "pools"
validators_table: str = "validators"
