# -*- coding: utf-8 -*-

from web3.contract.contract import ContractEvent

from src.globals import SDK
from src.classes import Trigger, Daemon
from src.daemons import BlockDaemon, EventDaemon, TimeDaemon
from src.triggers import (
    AlienationTrigger,
    DelegationTrigger,
    FallbackTrigger,
    InitiationTrigger,
    PoolsDBTrigger,
    StakeTrigger,
    DepositTrigger,
)

from src.utils import set_web3_account
from src.helpers.db_events import find_latest_event_block
from src.helpers.db_validators import (
    reinitialize_validators_table,
    fill_validators_table,
)
from src.helpers.db_pools import reinitialize_pools_table, fill_pools_table
from src.helpers.portal import get_all_owned_pubkeys, get_all_pool_ids
from src.globals.constants import hour_blocks


def init_dbs():
    """Initializes the databases and fills them with the current data.

    This function is called at the beginning of the program to make sure the
    databases are up to date.
    """
    # initialize pools table and fill it with current data
    reinitialize_pools_table()  # TODO: This will be removed after testing
    fill_pools_table(get_all_pool_ids())

    # initialize validators table and fill it with current data
    reinitialize_validators_table()  # TODO: This will be removed after testing
    fill_validators_table(get_all_owned_pubkeys())


def setup_daemons():
    """Initializes and runs the daemons for the triggers.

    This function is called at the beginning of the program to make sure the
    daemons are running.
    """
    # Triggers
    pools_db_trigger: PoolsDBTrigger = (
        PoolsDBTrigger()
    )  # TODO: This will be removed and db setup will be initialized on here.
    initiation_trigger: InitiationTrigger = InitiationTrigger()
    surplus_trigger: DepositTrigger = DepositTrigger()
    delegation_trigger: DelegationTrigger = DelegationTrigger()
    fallback_trigger: FallbackTrigger = FallbackTrigger()
    alienation_trigger: AlienationTrigger = AlienationTrigger()
    stake_trigger: StakeTrigger = StakeTrigger()

    events: ContractEvent = SDK.portal.contract.events

    # Create appropriate type of Daemons for the triggers
    initiation_daemon: EventDaemon = EventDaemon(
        triggers=[initiation_trigger],
        event=events.IdInitiated(),
        start_block=find_latest_event_block("IdInitiated"),
    )
    surplus_daemon: EventDaemon = EventDaemon(
        triggers=[surplus_trigger],
        event=events.Deposit(),
        start_block=find_latest_event_block("Deposit"),
    )
    delegation_daemon: EventDaemon = EventDaemon(
        triggers=[delegation_trigger],
        event=events.Delegation(),
        start_block=find_latest_event_block("Delegation"),
    )
    fallback_daemon: EventDaemon = EventDaemon(
        triggers=[fallback_trigger],
        event=events.FallbackOperator(),
        start_block=find_latest_event_block("FallbackOperator"),
    )
    alienation_daemon: EventDaemon = EventDaemon(
        triggers=[alienation_trigger],
        event=events.Alienated(),
        start_block=find_latest_event_block("Alienated"),
    )
    pools_db_daemon: TimeDaemon = TimeDaemon(
        interval=21600, triggers=[pools_db_trigger]
    )  # TODO: This will be removed after testing
    stake_daemon: BlockDaemon = BlockDaemon(
        triggers=[stake_trigger], block_period=12 * hour_blocks
    )

    # Run the daemons
    pools_db_daemon.run()
    initiation_daemon.run()
    surplus_daemon.run()
    delegation_daemon.run()
    fallback_daemon.run()
    alienation_daemon.run()
    # stake_daemon.run()


def main():
    """Main function of the program.

    This function is called when the program is run.

    It initializes the SDK, sets the web3 account, initializes the databases,
    and sets up the daemons.
    """

    # Utilize the SDK.w3 with privaded private key
    set_web3_account()

    # make sure database is ok
    init_dbs()

    # Initialize and run the daemons
    setup_daemons()


if __name__ == "__main__":
    main()
