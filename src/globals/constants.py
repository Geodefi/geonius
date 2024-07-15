# -*- coding: utf-8 -*-

from src.common.attribute_dict import AttributeDict
from src.globals import get_sdk, get_config


def init_constants():
    sdk = get_sdk()
    config = get_config()
    return AttributeDict.convert_recursive(
        {
            "chain": config.chains[sdk.network.name],
            "hour_blocks": 3600 // int(config.chains[sdk.network.name].interval),
            "one_minute": 60,
            "one_hour": 3600,
        }
    )
