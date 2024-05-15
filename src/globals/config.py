# -*- coding: utf-8 -*-

import json
import sys

from src.utils.attribute_dict import AttributeDict, convert_recursive
from src.globals.flags import flags
from src.globals.sdk import SDK
from src.utils.error import MissingConfigError


def __apply_flags(config: AttributeDict):
    """Applies the flags to the configuration. If a flag is not set, the configuration is not changed.

    Args:
        config (AttributeDict): the configuration as an AttributeDict.

    Returns:
        AttributeDict: the configuration with the flags applied.
    """

    if flags.no_log_stream:
        config.logger.file = False
    if flags.no_log_file:
        config.logger.file = False
    if flags.min_proposal_queue:
        # TODO:
        pass
    if flags.max_proposal_delay:
        # TODO:
        pass
    if flags.main_directory:
        config.directory = flags.main_directory
    if flags.logger_directory:
        config.logger.directory = flags.logger_directory
    if flags.logger_level:
        config.logger.level = flags.logger_level
    if flags.logger_when:
        config.logger.when = flags.logger_when
    if flags.logger_interval:
        config.logger.interval = flags.logger_interval
    if flags.logger_backup:
        config.logger.backup = flags.logger_backup
    if flags.database_directory:
        config.database.directory = flags.database_directory
    if flags.chain_start:
        config.chains[SDK.network.name].start = flags.chain_start
    if flags.chain_identifier:
        config.chains[SDK.network.name].identifier = flags.chain_identifier
    if flags.chain_period:
        config.chains[SDK.network.name].period = int(flags.chain_period)
    if flags.chain_interval:
        config.chains[SDK.network.name].interval = int(flags.chain_interval)
    if flags.chain_range:
        config.chains[SDK.network.name].range = int(flags.chain_range)
    if flags.ethdo_wallet:
        config.ethdo.wallet = flags.ethdo_wallet
    if flags.ethdo_account:
        config.ethdo.account = flags.ethdo_account

    return config


def __init_config() -> AttributeDict:
    """Initializes the configuration from the config.json file.

    Returns:
        AttributeDict: the configuration as an AttributeDict.

    Raises:
        TypeError: if the config file is not a dict after loading from json.
    """

    try:
        # catch configuration variables
        config_dict: dict = json.load(open("config.json", encoding="utf-8"))

        if not isinstance(config_dict, dict):
            raise TypeError("Config file should be a dict after loading from json, but it is not.")

    except Exception as e:
        # TODO: log error
        sys.exit(e)

    config: AttributeDict = convert_recursive(config_dict)

    return config


# global Config
CONFIG: AttributeDict = __apply_flags(__init_config())
