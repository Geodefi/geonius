# -*- coding: utf-8 -*-

from web3.contract.contract import ContractEvent

import os
from geodefi import Geode
from geodefi.globals.constants import ETHER_DENOMINATOR

from src.common import AttributeDict, Loggable
from src.exceptions import (
    ConfigurationFieldError,
    MissingConfigurationError,
    EthdoError,
    GasApiError,
)
from src.daemons import BlockDaemon, EventDaemon
from src.triggers.event import (
    AlienatedTrigger,
    DelegationTrigger,
    FallbackOperatorTrigger,
    IdInitiatedTrigger,
    DepositTrigger,
    StakeProposalTrigger,
    ExitRequestTrigger,
)
from src.triggers.block import (
    StakeTrigger,
)
from src.actions.ethdo import ping_account

from src.utils.gas import parse_gas, fetch_gas
from src.utils.notify import send_email

from src.helpers.portal import get_name
from src.globals import (
    set_config,
    set_sdk,
    set_constants,
    set_logger,
    get_config,
    get_sdk,
    get_logger,
    get_constants,
)
from src.helpers.portal import get_maintainer, get_wallet_balance

from src.globals.config import apply_flags, init_config
from src.globals.constants import init_constants
from src.globals.sdk import init_sdk

from src.database.pools import reinitialize_pools_table, create_pools_table
from src.database.operators import reinitialize_operators_table, create_operators_table
from src.database.validators import reinitialize_validators_table, create_validators_table
from src.database.events import (
    reinitialize_alienated_table,
    reinitialize_delegation_table,
    reinitialize_deposit_table,
    reinitialize_exit_request_table,
    reinitialize_stake_proposal_table,
    reinitialize_fallback_operator_table,
    reinitialize_id_initiated_table,
    create_alienated_table,
    create_delegation_table,
    create_deposit_table,
    create_exit_request_table,
    create_stake_proposal_table,
    create_fallback_operator_table,
    create_id_initiated_table,
)


def preflight_checks(test_email: bool = False, test_ethdo=False, test_operator=False):
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
    if not "chains" in config:
        raise MissingConfigurationError("'chains' section on config.json is missing or empty.")
    if not "network" in config:
        raise MissingConfigurationError("'network' section on config.json is missing or empty.")
    if not "strategy" in config:
        raise MissingConfigurationError("'strategy' section on config.json is missing or empty.")
    if not "logger" in config:
        raise MissingConfigurationError("'logger' section on config.json is missing or empty.")
    if not "database" in config:
        raise MissingConfigurationError("'database' section on config.json is missing or empty.")
    if not "ethdo" in config:
        raise MissingConfigurationError("'ethdo' section on config.json is missing or empty.")

    # Fields
    # TODO: (later) chain related checks should be implemented...
    # chain: AttributeDict = config.chains[config.chain_name] #

    network: AttributeDict = config.network
    if not "refresh_rate" in network:
        raise MissingConfigurationError("'network' section is missing the 'refresh_rate' field.")
    elif network.refresh_rate <= 0 or network.refresh_rate > 360:
        raise ConfigurationFieldError("Provided value is unexpected: (0-360] seconds")

    if not "max_attempt" in network:
        raise MissingConfigurationError("'network' section is missing the 'max_attempt' field.")
    elif network.max_attempt <= 0 or network.max_attempt > 100:
        raise ConfigurationFieldError("Provided value is unexpected: (0-100] attempts")

    if not "attempt_rate" in network:
        raise MissingConfigurationError("'network' section is missing the 'attempt_rate' field.")
    elif network.max_attempt <= 0 or network.attempt_rate > 10:
        raise ConfigurationFieldError("Provided value is unexpected: (0-10] seconds")

    strategy: AttributeDict = config.strategy
    if not "min_proposal_queue" in strategy:
        raise MissingConfigurationError(
            "'strategy' section is missing the 'min_proposal_queue' field."
        )
    elif strategy.min_proposal_queue < 0 or strategy.min_proposal_queue > 50:
        raise ConfigurationFieldError("Provided value is unexpected: [0-50] pubkeys")

    if not "max_proposal_delay" in strategy:
        raise MissingConfigurationError(
            "'strategy' section is missing the 'max_proposal_delay' field."
        )
    elif strategy.max_proposal_delay < 0 or strategy.max_proposal_delay > 604800:
        raise ConfigurationFieldError("Provided value is unexpected: [0-604800] seconds")

    logger: AttributeDict = config.logger
    if not "no_stream" in logger:
        raise MissingConfigurationError("'logger' section is missing the 'no_stream' field.")

    if not "no_file" in logger:
        raise MissingConfigurationError("'logger' section is missing the 'no_file' field.")

    if not "no_file" in logger:
        if not "level" in logger:  # can add more checks
            raise MissingConfigurationError("'logger' section is missing the 'level' field.")

        if not "when" in logger:  # can add more checks
            raise MissingConfigurationError("'logger' section is missing the 'when' field.")

        if not "interval" in logger:  # can add more checks
            raise MissingConfigurationError("'logger' section is missing the 'interval' field.")

        if not "backup" in logger:  # can add more checks
            raise MissingConfigurationError("'logger' section is missing the 'backup' field.")

    database: AttributeDict = config.database
    if not "dir" in database:
        raise MissingConfigurationError("'database' section is missing the 'dir' field.")

    if "gas" in config:
        gas: AttributeDict = config.gas
        if not "max_priority" in gas:
            raise MissingConfigurationError("'gas' section is missing the 'max_priority' field.")
        if not "max_fee" in gas:
            raise MissingConfigurationError("'gas' section is missing the 'max_fee' field.")
        if not "api" in gas:
            raise MissingConfigurationError("'gas' section is missing the 'api' field.")
        if not "parser" in gas:
            raise MissingConfigurationError(
                "No parser could be identified for the provided gas api"
            )

        priority_fee, base_fee = parse_gas(fetch_gas())
        if priority_fee is None or base_fee is None or priority_fee <= 0 or base_fee <= 0:
            raise GasApiError("Gas api did not respond or faulty")

    if test_ethdo:
        ethdo: AttributeDict = config.ethdo
        if not "wallet" in ethdo:
            raise MissingConfigurationError("'ethdo' section is missing the 'wallet' field.")
        if not "account" in ethdo:
            raise MissingConfigurationError("'ethdo' section is missing the 'account' field.")
        if not ping_account(wallet=ethdo.wallet, account=ethdo.account):
            raise EthdoError(f"Provided account: {ethdo.wallet}/{ethdo.account} does not exists.")

    if test_operator:
        sdk: Geode = get_sdk()
        signer = sdk.w3.eth.default_account
        maintainer = get_maintainer(config.operator_id)

        if maintainer != signer:
            raise ConfigurationFieldError(
                f"'maintainer' of {config.operator_id} is {maintainer}. Provided private key for {signer} does not match."
            )

        balance: int = get_wallet_balance(config.operator_id)

        get_logger().warning(
            f"{get_name(config.operator_id)} has {balance/ETHER_DENOMINATOR}ETH ({balance} wei) balance in portal."
            f" Use 'geonius increase-wallet' to deposit more."
        )

    if test_email:
        if "email" in config:
            email: AttributeDict = config.email

            if not "smtp_server" in email:
                raise MissingConfigurationError(
                    "'email' section is missing the required 'smtp_server' field."
                )
            if not "smtp_port" in email:
                raise MissingConfigurationError(
                    "'email' section is missing the required 'smtp_port' field."
                )
            if not "dont_notify_devs" in email:
                email.dont_notify_devs = False

                get_logger().info(f"Notification service is configured! Sending a test email...")
                send_email(
                    "Email notification service is active",
                    "Looks like geonius is functional and it is sailing smoothly at the moment."
                    "We will send you regular emails when something important happens or when there is an error."
                    "Don't forget to check your script regularly tho. This service can fail too!",
                    dont_notify_devs=True,
                )


def setup(**kwargs):
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
    flags: AttributeDict = AttributeDict({k: v for k, v in kwargs.items() if v is not None})

    config = apply_flags(init_config(flags.main_dir), flags)
    set_config(config)

    set_constants(init_constants())

    logger: Loggable = Loggable()
    set_logger(logger)

    set_sdk(
        init_sdk(
            exec_api=config.chains[config.chain_name].execution_api,
            cons_api=config.chains[config.chain_name].consensus_api,
            priv_key=os.getenv("GEONIUS_PRIVATE_KEY"),
        )
    )

    preflight_checks(
        test_email=kwargs["test_email"],
        test_ethdo=kwargs["test_ethdo"],
        test_operator=kwargs["test_operator"],
    )


def init_dbs(reset: bool = False):
    """Initializes the databases as suited.\
    This function is called at the beginning of the program to make sure the
    databases are up to date.

    Args:
        reset (bool, optional): Wipes out all data if provided. Defaults to False.
    """
    if reset:
        get_logger().warning("Dropping the database...")

        reinitialize_pools_table()
        reinitialize_operators_table()
        reinitialize_validators_table()

        reinitialize_alienated_table()
        reinitialize_delegation_table()
        reinitialize_deposit_table()
        reinitialize_exit_request_table()
        reinitialize_stake_proposal_table()
        reinitialize_fallback_operator_table()
        reinitialize_id_initiated_table()

    else:
        create_pools_table()
        create_operators_table()
        create_validators_table()

        create_alienated_table()
        create_delegation_table()
        create_deposit_table()
        create_exit_request_table()
        create_stake_proposal_table()
        create_fallback_operator_table()
        create_id_initiated_table()


def run_daemons():
    """Initializes and runs the daemons for the triggers.

    This function is called at the beginning of the program to make sure the
    daemons are running.
    """
    events: ContractEvent = get_sdk().portal.contract.events

    # Triggers
    id_initiated_trigger: IdInitiatedTrigger = IdInitiatedTrigger()
    deposit_trigger: DepositTrigger = DepositTrigger()
    delegation_trigger: DelegationTrigger = DelegationTrigger()
    stake_proposal_trigger: StakeProposalTrigger = StakeProposalTrigger()
    fallback_operator_trigger: FallbackOperatorTrigger = FallbackOperatorTrigger()
    alienated_trigger: AlienatedTrigger = AlienatedTrigger()
    # exit_request_trigger: ExitRequestTrigger = ExitRequestTrigger()
    # stake_trigger: StakeTrigger = StakeTrigger()

    # Create appropriate type of Daemons for the triggers
    id_initiated_daemon: EventDaemon = EventDaemon(
        trigger=id_initiated_trigger,
        event=events.IdInitiated(),
    )
    deposit_daemon: EventDaemon = EventDaemon(
        trigger=deposit_trigger,
        event=events.Deposit(),
    )
    delegation_daemon: EventDaemon = EventDaemon(
        trigger=delegation_trigger,
        event=events.Delegation(),
    )
    stake_proposal_daemon: EventDaemon = EventDaemon(
        trigger=stake_proposal_trigger,
        event=events.StakeProposal(),
    )
    fallback_operator_daemon: EventDaemon = EventDaemon(
        trigger=fallback_operator_trigger,
        event=events.FallbackOperator(),
    )
    alienated_daemon: EventDaemon = EventDaemon(
        trigger=alienated_trigger,
        event=events.Alienated(),
    )
    # exit_request_daemon: EventDaemon = EventDaemon(
    #     trigger=exit_request_trigger,
    #     event=events.ExitRequest(),
    # )
    # stake_daemon: BlockDaemon = BlockDaemon(
    #     trigger=stake_trigger, block_period=0.5 * get_constants().hour_blocks
    # )

    # Run the daemons
    id_initiated_daemon.run()
    deposit_daemon.run()
    delegation_daemon.run()
    stake_proposal_daemon.run()
    fallback_operator_daemon.run()
    alienated_daemon.run()
    # exit_request_daemon.run()
    # stake_daemon.run()
