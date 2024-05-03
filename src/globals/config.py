# -*- coding: utf-8 -*-

import json
from src.utils.attribute_dict import AttributeDict, convert_recursive
from src.globals.exceptions import MissingConfigException

# catch configuration variables
config_dict: dict = json.load(open("config.json", encoding="utf-8"))

# turn the config into AttributeDict recursively, so we can use dot notation
CONFIG: AttributeDict
if not dict:
    raise MissingConfigException
else:
    CONFIG = convert_recursive(config_dict)

# TODO: take flag params here, and change CONFIG accordingly!
# Nice!
