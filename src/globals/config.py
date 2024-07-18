# -*- coding: utf-8 -*-

from os import path
import json

from src.common import AttributeDict
from src.exceptions import ConfigurationFileError, MissingConfigurationError


def apply_flags(
    flags: AttributeDict,
    config: AttributeDict,
    env: AttributeDict,
):
    """Applies the flags to the configuration.
    If a particular flag is not set, the configuration is not changed.

    Args:
        config (AttributeDict): the configuration as an AttributeDict.

    Returns:
        AttributeDict: the configuration with the flags applied.
    """
    flags = AttributeDict({k: v for k, v in flags.items() if v is not None})

    if "no_log_stream" in flags:
        config.logger.no_stream = flags.no_log_stream
    if "no_log_file" in flags:
        config.logger.no_file = flags.no_log_file
    if "min_proposal_queue" in flags:
        config.strategy.min_proposal_queue = flags.min_proposal_queue
    if "max_proposal_delay" in flags:
        config.strategy.max_proposal_delay = flags.max_proposal_delay
    if "network_refresh_rate" in flags:
        config.network.refresh_rate = flags.network_refresh_rate
    if "network_max_attempt" in flags:
        config.network.max_attempt = flags.network_max_attempt
    if "network_attempt_rate" in flags:
        config.network.attempt_rate = flags.network_attempt_rate
    if "logger_directory" in flags:
        config.logger.directory = flags.logger_directory
    if "logger_level" in flags:
        config.logger.level = flags.logger_level
    if "logger_when" in flags:
        config.logger.when = flags.logger_when
    if "logger_interval" in flags:
        config.logger.interval = flags.logger_interval
    if "logger_backup" in flags:
        config.logger.backup = flags.logger_backup
    if "database_directory" in flags:
        config.database.directory = flags.database_directory
    if "ethdo_wallet" in flags:
        config.ethdo.wallet = flags.ethdo_wallet
    if "ethdo_account" in flags:
        config.ethdo.account = flags.ethdo_account

    if "dont_notify_devs" in flags:
        if flags.dont_notify_devs is True:
            try:
                config.email.dont_notify_devs = flags.dont_notify_devs
            except Exception as e:
                raise MissingConfigurationError(
                    "'--dont-notify-devs' flag requires email configuration"
                ) from e
    if "chain_start" in flags:
        config.chains[flags.chain].start = flags.chain_start
    if "chain_identifier" in flags:
        config.chains[flags.chain].identifier = flags.chain_identifier
    if "chain_period" in flags:
        config.chains[flags.chain].period = int(flags.chain_period)
    if "chain_interval" in flags:
        config.chains[flags.chain].interval = int(flags.chain_interval)
    if "chain_range" in flags:
        config.chains[flags.chain].range = int(flags.chain_range)

    # put the execution api key in configuration from environment variables
    if "<EXECUTION_API_KEY>" in config.chains[flags.chain].execution_api:
        if env.EXECUTION_API_KEY:
            config.chains[flags.chain].execution_api = config.chains[
                flags.chain
            ].execution_api.replace("<EXECUTION_API_KEY>", env.EXECUTION_API_KEY)
        else:
            raise MissingConfigurationError("EXECUTION_API_KEY environment var should be provided.")

    # put the consensus api key in configuration from environment variables
    if "<CONSENSUS_API_KEY>" in config.chains[flags.chain].consensus_api:
        if env.CONSENSUS_API_KEY:
            config.chains[flags.chain].consensus_api = config.chains[
                flags.chain
            ].consensus_api.replace("<CONSENSUS_API_KEY>", env.CONSENSUS_API_KEY)
        else:
            raise MissingConfigurationError("CONSENSUS_API_KEY environment var should be provided.")

        # put the gas api key in configuration from environment variables
        if 'gas' in config:
            if "<GAS_API_KEY>" in config.gas.api:
                if env.GAS_API_KEY:
                    config.gas.api = config.gas.api.replace("<GAS_API_KEY>", env.GAS_API_KEY)
                else:
                    raise MissingConfigurationError(
                        "GAS_API_KEY environment var should be provided."
                    )

    return config


def init_config(main_dir: str) -> AttributeDict:
    """Initializes the configuration from the config.json file from main directory.

    Returns:
        AttributeDict: the configuration as an AttributeDict.

    Raises:
        TypeError: if the config file is not a dict after loading from json.
    """

    try:
        config_path = path.join(main_dir, 'config.json')

        # Catch configuration variables
        config_dict: dict = json.load(open(config_path, encoding="utf-8"))

        # Set main_directory as a config param
        config_dict["directory"] = main_dir

        config: AttributeDict = AttributeDict.convert_recursive(config_dict)

    except Exception as e:
        raise ConfigurationFileError(
            "Error while loading the configuration file 'config.json'"
        ) from e

    return config
