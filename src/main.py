# -*- coding: utf-8 -*-

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
    SurplusTrigger,
)

from src.utils import set_web3_account
from src.helpers.db_validators import (
    reinitialize_validators_table,
    fill_validators_table,
)
from src.helpers.db_pools import reinitialize_pools_table, fill_pools_table
from src.helpers.portal import get_all_owned_pubkeys, get_all_pool_ids


def init_dbs():
    # initialize pools table and fill it with current data
    reinitialize_pools_table()
    fill_pools_table(get_all_pool_ids())

    # initialize validators table and fill it with current data
    reinitialize_validators_table()
    fill_validators_table(get_all_owned_pubkeys())


def setup_daemons():
    # Triggers
    pools_db_trigger = PoolsDBTrigger()
    initiation_trigger = InitiationTrigger()
    surplus_trigger = SurplusTrigger()
    delegation_trigger = DelegationTrigger()
    fallback_trigger = FallbackTrigger()
    alienation_trigger = AlienationTrigger()
    stake_trigger = StakeTrigger()

    events = SDK.portal.events

    # Create appropriate type of Daemons for the triggers
    # pools_db_daemon should run every 6 hours and update all the pools data
    initiation_daemon = EventDaemon(
        triggers=[initiation_trigger], event=events.IdInitiated()
    )
    surplus_daemon = EventDaemon(triggers=[surplus_trigger], event=events.Deposit())
    delegation_daemon = EventDaemon(
        triggers=[delegation_trigger], event=events.Delegation()
    )
    fallback_daemon = EventDaemon(
        triggers=[fallback_trigger], event=events.FallbackOperator()
    )
    alienation_daemon = EventDaemon(
        triggers=[alienation_trigger], event=events.Alienated()
    )
    pools_db_daemon = TimeDaemon(interval=21600, triggers=[pools_db_trigger])
    # stake_daemon = EventDaemon(triggers=[stake_trigger], event=events.IdInitiated()) todo

    # Run the daemons
    pools_db_daemon.run()
    initiation_daemon.run()
    surplus_daemon.run()
    delegation_daemon.run()
    fallback_daemon.run()
    alienation_daemon.run()
    # stake_daemon.run()


def main():
    # Utilize the SDK.w3 with privaded private key
    set_web3_account()

    # make sure database is ok
    init_dbs()

    # Initialize and run the daemons
    setup_daemons()


if __name__ == "__main__":
    main()
