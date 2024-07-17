from typing import Callable

from geodefi import Geode
from geodefi.globals.constants import ETHER_DENOMINATOR

from src.common import AttributeDict, Loggable
from src.exceptions import (
    ConfigurationFieldError,
    MissingConfigurationError,
    EthdoError,
    GasApiError,
)
from src.actions.ethdo import ping_account
from src.utils.gas import parse_gas, fetch_gas
from src.helpers.portal import get_name
from src.globals import (
    set_config,
    set_env,
    set_sdk,
    set_flags,
    set_constants,
    set_logger,
    get_flags,
    get_env,
    get_config,
    get_sdk,
    get_logger,
)
from src.helpers.portal import get_maintainer, get_wallet_balance
from src.globals.config import apply_flags, init_config
from src.globals.constants import init_constants
from src.globals.env import load_env
from src.globals.flags import collect_flags
from src.globals.sdk import init_sdk


def preflight_checks():
    """Checks if everything is ready for geonius to work.
    - Checks if config missing any values. 'gas' and 'email' sections are optional,
        however they should be valid if provided.
    - Checks if ethdo is available and account exists
    - Checks if gas api working, when provided
    - Checks if given private key can control the provided Operator ID
    - Checks if there is enough money in the operator wallet and prints

    Raises:
        MissingConfigurationError: One of the required fields on configuration file is missing.
    """
    config = get_config()

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
    if not 'wallet' in ethdo:
        raise MissingConfigurationError("'ethdo' section is missing the 'wallet' field.")
    if not 'account' in ethdo:
        raise MissingConfigurationError("'ethdo' section is missing the 'account' field.")
    if not ping_account(wallet=ethdo.wallet, account=ethdo.account):
        raise EthdoError(f"Provided account: {ethdo.wallet}/{ethdo.account} does not exists.")

    if "gas" in config:
        gas: AttributeDict = config.gas
        if not 'max_priority' in gas:
            raise MissingConfigurationError("'gas' section is missing the 'max_priority' field.")
        if not 'max_fee' in gas:
            raise MissingConfigurationError("'gas' section is missing the 'max_fee' field.")
        if not 'api' in gas:
            raise MissingConfigurationError("'gas' section is missing the 'api' field.")
        if not 'parser' in gas:
            raise MissingConfigurationError(
                "No parser could be identified for the provided gas api"
            )

        priority_fee, base_fee = parse_gas(fetch_gas())
        if priority_fee is None or base_fee is None or priority_fee <= 0 or base_fee <= 0:
            raise GasApiError("Gas api did not respond or faulty")

    if "email" in config:
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

    sdk: Geode = get_sdk()
    signer = sdk.w3.eth.default_account
    maintainer = get_maintainer(config.operator_id)

    if maintainer != signer:
        raise ConfigurationFieldError(
            f"'maintainer' of {config.operator_id} is {maintainer}. Provided private key for {signer} does not match."
        )

    balance: int = get_wallet_balance(config.operator_id)

    get_logger().warning(
        f"{get_name(config.operator_id)} has {balance/ETHER_DENOMINATOR} ETH ({balance} wei) in the internal wallet. Use 'geonius increase-wallet --value X --chain X' to deposit more."
    )


def setup(flag_collector: Callable = collect_flags):
    """Initializes the required components from the geonius script:
    - Loads environment variables from specified .env file
    - Applies the provided flags to be utilized in the config step
    - Creates a config dict from provided json
    - Configures the geodefi python sdk
    - Configures the constant parameters for ease of use

    Args:
        flag_collector (Callable): a fuunction that provides the will
        provide the provided flags with the help of argparse lib.
        Secondary scripts can have their own flags, then this should be speciifed.
        Otherwise, defaults to collect_flags.
    """
    set_flags(flag_collector())
    set_env(load_env())

    config = apply_flags(init_config())
    set_config(config)

    set_logger(Loggable())
    set_sdk(
        init_sdk(
            exec_api=get_config().chains[get_flags().chain].execution_api,
            cons_api=get_config().chains[get_flags().chain].consensus_api,
            priv_key=get_env().PRIVATE_KEY,
        )
    )
    set_constants(init_constants())
    preflight_checks()
