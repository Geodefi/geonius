# -*- coding: utf-8 -*-

import json
from src.utils.attribute_dict import AttributeDict, convert_recursive
from src.globals.exceptions import MissingConfigException


def __init_config() -> AttributeDict:
    # TODO: take flag params here, and change CONFIG accordingly!

    # catch configuration variables
    config_dict: dict = json.load(open("config.json", encoding="utf-8"))

    # turn the config into AttributeDict recursively, so we can use dot notation
    config: AttributeDict
    print(dict)
    if not isinstance(config_dict, dict):
        raise MissingConfigException
    else:
        config = convert_recursive(config_dict)

    # Check for config.json on abs home, then change according to flags
    return config


# global Config
CONFIG: AttributeDict = __init_config()
