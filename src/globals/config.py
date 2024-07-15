# -*- coding: utf-8 -*-

from os import path
import json
import geodefi

from src.common import AttributeDict
from src.exceptions import (
    ConfigurationFileError,
    MissingConfigurationError,
    ConfigurationFieldError,
)


from src.globals import get_flags, get_env


def apply_flags(config: AttributeDict):
    """Applies the flags to the configuration. If a flag is not set, the configuration is not changed.

    Args:
        config (AttributeDict): the configuration as an AttributeDict.

    Returns:
        AttributeDict: the configuration with the flags applied.
    """
    flags = AttributeDict({k: v for k, v in get_flags().items() if v is not None})

    if "no_log_stream" in flags:
        config.logger.no_stream = flags.no_log_stream
    if "no_log_file" in flags:
        config.logger.no_file = flags.no_log_file
    if "min_proposal_queue" in flags:
        config.strategy.min_proposal_queue = flags.min_proposal_queue
    if "max_proposal_delay" in flags:
        config.strategy.max_proposal_delay = flags.max_proposal_delay
    if "network_refresh_rate" in flags:
        geodefi.globals.constants.REFRESH_RATE = flags.network_max_attempt
    if "network_attempt_rate" in flags:
        geodefi.globals.constants.ATTEMPT_RATE = flags.network_attempt_rate
    if "network_max_attempt" in flags:
        geodefi.globals.constants.MAX_ATTEMPT = flags.network_refresh_rate
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
    if "ethdo_wallet" in flags:
        config.ethdo.wallet = flags.ethdo_wallet
    if "ethdo_account" in flags:
        config.ethdo.account = flags.ethdo_account
    if "dont_notify_devs" in flags:
        config.email.dont_notify_devs = flags.dont_notify_devs

    # put the gas api key in the configuration from the environment variables
    if "<GAS_API_KEY>" in config.gas.api and get_env().GAS_API_KEY:
        config.gas.api = config.gas.api.replace("<GAS_API_KEY>", get_env().GAS_API_KEY)
    elif "<GAS_API_KEY>" in config.gas.api:
        raise MissingConfigurationError("GAS_API_KEY environment var should be provided.")
    return config


def preflight_checks(config: AttributeDict):
    """Checks if the config.json file is missing any values. 'gas' and 'email' sections are Optional,
    however they should be valid if provided.  # TODO: (now) check if they are optional in the code as well

    Args:
        config (AttributeDict): Provided config.json as a dictionary

    Raises:
        MissingConfigurationError: One of the required fields on configuration file is missing.
    """
    # Sections
    if not 'chains' in config:
        raise MissingConfigurationError("'chains' section on config.json is missing or empty.")
    if not 'network' in config:
        raise MissingConfigurationError("'network' section on config.json is missing or empty.")
    if not 'strategy' in config:
        raise MissingConfigurationError("'strategy' section on config.json is missing or empty.")
    if not 'logger' in config:
        raise MissingConfigurationError("'logger' section on config.json is missing or empty.")
    if not 'database' in config:
        raise MissingConfigurationError("'database' section on config.json is missing or empty.")
    if not 'ethdo' in config:
        raise MissingConfigurationError("'ethdo' section on config.json is missing or empty.")

    # Fields
    # TODO: (later) chain related checks should be implemented...
    # chain: AttributeDict = config.chains[get_flags().chain] #

    network: AttributeDict = config.network
    if not 'refresh_rate' in network:
        raise MissingConfigurationError("'network' section is missing the 'refresh_rate' field.")
    elif network.refresh_rate <= 0 or network.refresh_rate > 360:
        raise ConfigurationFieldError("Provided value is unexpected: (0-360] seconds")

    if not 'max_attempt' in network:
        raise MissingConfigurationError("'network' section is missing the 'max_attempt' field.")
    elif network.max_attempt <= 0 or network.max_attempt > 100:
        raise ConfigurationFieldError("Provided value is unexpected: (0-100] attempts")

    if not 'attempt_rate' in network:
        raise MissingConfigurationError("'network' section is missing the 'attempt_rate' field.")
    elif network.max_attempt <= 0 or network.attempt_rate > 10:
        raise ConfigurationFieldError("Provided value is unexpected: (0-10] seconds")

    strategy: AttributeDict = config.strategy
    if not 'min_proposal_queue' in strategy:
        raise MissingConfigurationError(
            "'strategy' section is missing the 'min_proposal_queue' field."
        )
    elif strategy.min_proposal_queue < 0 or strategy.min_proposal_queue > 50:
        raise ConfigurationFieldError("Provided value is unexpected: [0-50] pubkeys")

    if not 'max_proposal_delay' in strategy:
        raise MissingConfigurationError(
            "'strategy' section is missing the 'max_proposal_delay' field."
        )
    elif strategy.max_proposal_delay < 0 or strategy.max_proposal_delay > 604800:
        raise ConfigurationFieldError("Provided value is unexpected: [0-604800] seconds")

    logger: AttributeDict = config.logger
    if not 'no_stream' in logger:
        raise MissingConfigurationError("'logger' section is missing the 'no_stream' field.")

    if not 'no_file' in logger:
        raise MissingConfigurationError("'logger' section is missing the 'no_file' field.")

    if not 'no_file' in logger:
        if not 'level' in logger:  # can add more checks
            raise MissingConfigurationError("'logger' section is missing the 'level' field.")

        if not 'when' in logger:  # can add more checks
            raise MissingConfigurationError("'logger' section is missing the 'when' field.")

        if not 'interval' in logger:  # can add more checks
            raise MissingConfigurationError("'logger' section is missing the 'interval' field.")

        if not 'backup' in logger:  # can add more checks
            raise MissingConfigurationError("'logger' section is missing the 'backup' field.")

    database: AttributeDict = config.database
    if not 'directory' in database:
        raise MissingConfigurationError("'database' section is missing the 'directory' field.")

    ethdo: AttributeDict = config.ethdo
    if not 'wallet' in ethdo:  # TODO: (now) check if exists
        raise MissingConfigurationError("'ethdo' section is missing the 'wallet' field.")
    if not 'account' in ethdo:  # TODO: (now) check if exists
        raise MissingConfigurationError("'ethdo' section is missing the 'account' field.")

    if config.gas:
        gas: AttributeDict = config.gas
        if not 'max_priority' in gas:
            raise MissingConfigurationError("'gas' section is missing the 'max_priority' field.")
        if not 'max_fee' in gas:
            raise MissingConfigurationError("'gas' section is missing the 'max_fee' field.")
        if gas.api:  # Optional
            if not 'parser' in gas:
                raise MissingConfigurationError(
                    "No parser could be identified for the provided gas api"
                )
            # elif # TODO: (now) check if it is working.

    if config.email:
        email: AttributeDict = config.email

        if not 'smtp_server' in email:
            raise MissingConfigurationError(
                "'email' section is missing the required 'smtp_server' field."
            )
        if not 'smtp_port' in email:
            raise MissingConfigurationError(
                "'email' section is missing the required 'smtp_port' field."
            )
        if not 'dont_notify_devs' in email:
            email.dont_notify_devs = False


def init_config() -> AttributeDict:
    """Initializes the configuration from the config.json file from main directory.

    Returns:
        AttributeDict: the configuration as an AttributeDict.

    Raises:
        TypeError: if the config file is not a dict after loading from json.
    """

    try:
        main_dir: str = get_flags().main_directory
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
