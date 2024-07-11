# -*- coding: utf-8 -*-

import json
import geodefi

from src.common import AttributeDict
from src.exceptions import ConfigurationError

from src.globals import get_sdk, get_flags, get_env


def apply_flags(config: AttributeDict):
    """Applies the flags to the configuration. If a flag is not set, the configuration is not changed.

    Args:
        config (AttributeDict): the configuration as an AttributeDict.

    Returns:
        AttributeDict: the configuration with the flags applied.
    """
    flags = get_flags()
    sdk = get_sdk()
    if hasattr(flags, 'no_log_stream') and flags.no_log_stream:
        config.logger.stream = False
    if hasattr(flags, 'no_log_stream') and flags.no_log_file:
        config.logger.file = False
    if hasattr(flags, 'main_directory') and flags.main_directory:
        config.directory = flags.main_directory
    if hasattr(flags, 'min_proposal_queue') and flags.min_proposal_queue:
        config.strategy.min_proposal_queue = flags.min_proposal_queue
    if hasattr(flags, 'max_proposal_delay') and flags.max_proposal_delay:
        config.strategy.max_proposal_delay = flags.max_proposal_delay
    if hasattr(flags, 'network_refresh_rate') and flags.network_refresh_rate:
        geodefi.globals.constants.REFRESH_RATE = flags.network_max_attempt
    if hasattr(flags, 'network_attempt_rate') and flags.network_attempt_rate:
        geodefi.globals.constants.ATTEMPT_RATE = flags.network_attempt_rate
    if hasattr(flags, 'network_max_attempt') and flags.network_max_attempt:
        geodefi.globals.constants.MAX_ATTEMPT = flags.network_refresh_rate
    if hasattr(flags, 'logger_directory') and flags.logger_directory:
        config.logger.directory = flags.logger_directory
    if hasattr(flags, 'logger_level') and flags.logger_level:
        config.logger.level = flags.logger_level
    if hasattr(flags, 'logger_when') and flags.logger_when:
        config.logger.when = flags.logger_when
    if hasattr(flags, 'logger_interval') and flags.logger_interval:
        config.logger.interval = flags.logger_interval
    if hasattr(flags, 'logger_backup') and flags.logger_backup:
        config.logger.backup = flags.logger_backup
    if hasattr(flags, 'database_directory') and flags.database_directory:
        config.database.directory = flags.database_directory
    if hasattr(flags, 'chain_start') and flags.chain_start:
        config.chains[sdk.network.name].start = flags.chain_start
    if hasattr(flags, 'chain_identifier') and flags.chain_identifier:
        config.chains[sdk.network.name].identifier = flags.chain_identifier
    if hasattr(flags, 'chain_period') and flags.chain_period:
        config.chains[sdk.network.name].period = int(flags.chain_period)
    if hasattr(flags, 'chain_interval') and flags.chain_interval:
        config.chains[sdk.network.name].interval = int(flags.chain_interval)
    if hasattr(flags, 'chain_range') and flags.chain_range:
        config.chains[sdk.network.name].range = int(flags.chain_range)
    if hasattr(flags, 'ethdo_wallet') and flags.ethdo_wallet:
        config.ethdo.wallet = flags.ethdo_wallet
    if hasattr(flags, 'ethdo_account') and flags.ethdo_account:
        config.ethdo.account = flags.ethdo_account
    if hasattr(flags, 'dont_notify_geode') and flags.dont_notify_geode is False:
        config.email.dont_notify_geode = True

    # put the gas api key in the configuration from the environment variables
    if "<GAS_API_KEY>" in config.gas.api and get_env().GAS_API_KEY:
        config.gas.api = config.gas.api.replace("<GAS_API_KEY>", get_env().GAS_API_KEY)
    elif "<GAS_API_KEY>" in config.gas.api:
        raise ConfigurationError("GAS_API_KEY environment variable is not set.")

    return config


def init_config() -> AttributeDict:
    """Initializes the configuration from the geonius.json file.

    Returns:
        AttributeDict: the configuration as an AttributeDict.

    Raises:
        TypeError: if the config file is not a dict after loading from json.
    """

    try:
        config_path = "geonius.json"

        try:
            flags = get_flags()
            if hasattr(flags, 'config_path') and flags.config_path:
                config_path = flags.config_path
        except:
            pass

        # catch configuration variables
        config_dict: dict = json.load(open(config_path, encoding="utf-8"))

        if not isinstance(config_dict, dict):
            raise TypeError("Config file should be a dict after loading from json, but it is not.")

        config: AttributeDict = AttributeDict.convert_recursive(config_dict)

    except Exception as e:
        raise ConfigurationError("Error loading configuration file `geonius.json`.") from e

    return config
