# -*- coding: utf-8 -*-
from .config import CONFIG
from .sdk import SDK

hour_blocks: int = 3600 // int(CONFIG.chains[SDK.network.name].interval)
