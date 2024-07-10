# so we will have get_flags, get_constants etc and set_flags, set_constants etc as well. then it should be easy fixing 30 files with 35 imports. I wonder how we can do that faster.
from src.common.attribute_dict import AttributeDict

from src.globals import get_sdk, get_config


def init_constants():
    sdk = get_sdk()
    config = get_config()
    # catch environment variables
    return AttributeDict.convert_recursive(
        {
            "network": sdk.network.name,
            "chain": config.chains[sdk.network.name],
            "hour_blocks": 3600 // int(config.chains[sdk.network.name].interval),
            "one_minute": 60,
            "one_hour": 3600,
        }
    )
