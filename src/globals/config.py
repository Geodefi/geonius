# -*- coding: utf-8 -*-

import json
import geodefi

from src.common import AttributeDict
from src.exceptions import ConfigurationError

from .sdk import SDK
from .flags import FLAGS
from .env import GAS_API_KEY


def __apply_flags(config: AttributeDict):
    """Applies the flags to the configuration. If a flag is not set, the configuration is not changed.

    Args:
        config (AttributeDict): the configuration as an AttributeDict.

    Returns:
        AttributeDict: the configuration with the flags applied.
    """

    if FLAGS.no_log_stream:
        config.logger.stream = False
    if FLAGS.no_log_file:
        config.logger.file = False
    if FLAGS.main_directory:
        config.directory = FLAGS.main_directory
    if FLAGS.min_proposal_queue:
        config.min_proposal_queue = FLAGS.min_proposal_queue
    if FLAGS.max_proposal_delay:
        config.max_proposal_delay = FLAGS.max_proposal_delay
    if FLAGS.network_refresh_rate:
        geodefi.globals.constants.REFRESH_RATE = FLAGS.network_max_attempt
    if FLAGS.network_attempt_rate:
        geodefi.globals.constants.ATTEMPT_RATE = FLAGS.network_attempt_rate
    if FLAGS.network_max_attempt:
        geodefi.globals.constants.MAX_ATTEMPT = FLAGS.network_refresh_rate
    if FLAGS.logger_directory:
        config.logger.directory = FLAGS.logger_directory
    if FLAGS.logger_level:
        config.logger.level = FLAGS.logger_level
    if FLAGS.logger_when:
        config.logger.when = FLAGS.logger_when
    if FLAGS.logger_interval:
        config.logger.interval = FLAGS.logger_interval
    if FLAGS.logger_backup:
        config.logger.backup = FLAGS.logger_backup
    if FLAGS.database_directory:
        config.database.directory = FLAGS.database_directory
    if FLAGS.chain_start:
        config.chains[SDK.network.name].start = FLAGS.chain_start
    if FLAGS.chain_identifier:
        config.chains[SDK.network.name].identifier = FLAGS.chain_identifier
    if FLAGS.chain_period:
        config.chains[SDK.network.name].period = int(FLAGS.chain_period)
    if FLAGS.chain_interval:
        config.chains[SDK.network.name].interval = int(FLAGS.chain_interval)
    if FLAGS.chain_range:
        config.chains[SDK.network.name].range = int(FLAGS.chain_range)
    if FLAGS.ethdo_wallet:
        config.ethdo.wallet = FLAGS.ethdo_wallet
    if FLAGS.ethdo_account:
        config.ethdo.account = FLAGS.ethdo_account
    if FLAGS.not_notify_geode is False:
        config.email.notify_geode = False

    # put the gas api key in the configuration from the environment variables
    if "<GAS_API_KEY>" in config.gas.api and GAS_API_KEY:
        config.gas.api = config.gas.api.replace("<GAS_API_KEY>", GAS_API_KEY)
    elif "<GAS_API_KEY>" in config.gas.api:
        raise ConfigurationError("GAS_API_KEY environment variable is not set.")

    return config


def __init_config() -> AttributeDict:
    """Initializes the configuration from the geonius.json file.

    Returns:
        AttributeDict: the configuration as an AttributeDict.

    Raises:
        TypeError: if the config file is not a dict after loading from json.
    """

    try:
        config_path = "geonius.json"
        if FLAGS.config_path:
            config_path = FLAGS.config_path

        # catch configuration variables
        config_dict: dict = json.load(open(config_path, encoding="utf-8"))

        if not isinstance(config_dict, dict):
            raise TypeError("Config file should be a dict after loading from json, but it is not.")

        config: AttributeDict = AttributeDict.convert_recursive(config_dict)

    except Exception as e:
        raise ConfigurationError("Error loading configuration file `geonius.json`.") from e

    return config


# global Config
CONFIG: AttributeDict = __apply_flags(__init_config())
