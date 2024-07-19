# -*- coding: utf-8 -*-

import os
from os import getenv
import json

from src.common import AttributeDict
from src.exceptions import ConfigurationFileError, MissingConfigurationError


def apply_flags(
    config: AttributeDict,
    flags: AttributeDict,
):
    """Applies the flags to the configuration.
    If a particular flag is not set, the configuration is not changed.

    Args:
        config (AttributeDict): the configuration as an AttributeDict.

    Returns:
        AttributeDict: the configuration with the flags applied.
    """
    config.dir = flags.main_dir
    config.chain_name = flags.chain

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
    if "logger_dir" in flags:
        config.logger.dir = flags.logger_dir
    if "logger_level" in flags:
        config.logger.level = flags.logger_level
    if "logger_when" in flags:
        config.logger.when = flags.logger_when
    if "logger_interval" in flags:
        config.logger.interval = flags.logger_interval
    if "logger_backup" in flags:
        config.logger.backup = flags.logger_backup
    if "database_dir" in flags:
        config.database.dir = flags.database_dir
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
        config.chains[config.chain_name].start = flags.chain_start
    if "chain_identifier" in flags:
        config.chains[config.chain_name].identifier = flags.chain_identifier
    if "chain_period" in flags:
        config.chains[config.chain_name].period = int(flags.chain_period)
    if "chain_interval" in flags:
        config.chains[config.chain_name].interval = int(flags.chain_interval)
    if "chain_range" in flags:
        config.chains[config.chain_name].range = int(flags.chain_range)

    # put the execution api key in configuration from environment variables
    if "<API_KEY_EXECUTION>" in config.chains[flags.chain].execution_api:
        if getenv("API_KEY_EXECUTION"):
            config.chains[config.chain_name].execution_api = config.chains[
                config.chain_name
            ].execution_api.replace("<API_KEY_EXECUTION>", getenv("API_KEY_EXECUTION"))
        else:
            raise MissingConfigurationError("API_KEY_EXECUTION environment var should be provided.")

    # put the consensus api key in configuration from environment variables
    if "<API_KEY_CONSENSUS>" in config.chains[config.chain_name].consensus_api:
        if getenv("API_KEY_CONSENSUS"):
            config.chains[config.chain_name].consensus_api = config.chains[
                config.chain_name
            ].consensus_api.replace("<API_KEY_CONSENSUS>", getenv("API_KEY_CONSENSUS"))
        else:
            raise MissingConfigurationError("API_KEY_CONSENSUS environment var should be provided.")

        # put the gas api key in configuration from environment variables
        if "gas" in config:
            if "<API_KEY_GAS>" in config.gas.api:
                if getenv("API_KEY_GAS"):
                    config.gas.api = config.gas.api.replace("<API_KEY_GAS>", getenv("API_KEY_GAS"))
                else:
                    raise MissingConfigurationError(
                        "API_KEY_GAS environment var should be provided."
                    )

    return config


def init_config(main_dir: str) -> AttributeDict:
    """Initializes the configuration from the config.json file from main directory.

    Returns:
        AttributeDict: the configuration as an AttributeDict.

    Raises:
        TypeError: if the config file is not a dict after loading from json.
    """
    main_dir_path = os.path.join(os.getcwd(), main_dir)  # TODO: this can be home or cwd

    if not os.path.exists(main_dir_path):
        # TODO: log.error and ask if want to create
        raise ConfigurationFileError(
            f"Could not locate the provided path for the main directory: {main_dir_path}"
        )

    config_path = os.path.join(main_dir_path, "config.json")

    if os.path.exists(config_path):
        # Catch configuration variables
        try:
            config_dict: dict = json.load(open(config_path, encoding="utf-8"))
        except Exception as e:
            raise ConfigurationFileError(
                "Error while loading the configuration file 'config.json'"
            ) from e

    else:
        # TODO: log.error and ask if want to create
        raise ConfigurationFileError(f"Could not find a config.json file in {main_dir_path}")

    config: AttributeDict = AttributeDict.convert_recursive(config_dict)

    return config
