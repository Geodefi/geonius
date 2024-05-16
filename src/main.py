# -*- coding: utf-8 -*-
import sys

from web3.contract.contract import ContractEvent

from src.globals import SDK, hour_blocks, log
from src.daemons import BlockDaemon, EventDaemon
from src.triggers import (
    AlienatedTrigger,
    DelegationTrigger,
    FallbackOperatorTrigger,
    IdInitiatedTrigger,
    PoolsDBTrigger,
    StakeTrigger,
    DepositTrigger,
    ExitRequestTrigger,
)
from src.helpers import (
    find_latest_event_block,
    reinitialize_validators_table,
    fill_validators_table,
    reinitialize_pools_table,
    fill_pools_table,
    get_all_owned_pubkeys,
    get_all_pool_ids,
)


def init_dbs():
    """Initializes the databases and fills them with the current data.

    This function is called at the beginning of the program to make sure the
    databases are up to date.
    """
    log.debug("Initializing ")
    log.info("Initializing info")

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
    id_initiated_trigger: IdInitiatedTrigger = IdInitiatedTrigger()
    deposit_trigger: DepositTrigger = DepositTrigger()
    delegation_trigger: DelegationTrigger = DelegationTrigger()
    fallback_operator_trigger: FallbackOperatorTrigger = FallbackOperatorTrigger()
    alienated_trigger: AlienatedTrigger = AlienatedTrigger()
    stake_trigger: StakeTrigger = StakeTrigger()
    exit_request_trigger: ExitRequestTrigger = ExitRequestTrigger()

    events: ContractEvent = SDK.portal.contract.events

    # Create appropriate type of Daemons for the triggers
    id_initiated_daemon: EventDaemon = EventDaemon(
        trigger=id_initiated_trigger,
        event=events.IdInitiated(),
        start_block=find_latest_event_block("IdInitiated"),
    )
    deposit_deamon: EventDaemon = EventDaemon(
        trigger=deposit_trigger,
        event=events.Deposit(),
        start_block=find_latest_event_block("Deposit"),
    )
    delegation_daemon: EventDaemon = EventDaemon(
        trigger=delegation_trigger,
        event=events.Delegation(),
        start_block=find_latest_event_block("Delegation"),
    )
    fallback_operator_daemon: EventDaemon = EventDaemon(
        trigger=fallback_operator_trigger,
        event=events.FallbackOperator(),
        start_block=find_latest_event_block("FallbackOperator"),
    )
    alienated_daemon: EventDaemon = EventDaemon(
        trigger=alienated_trigger,
        event=events.Alienated(),
        start_block=find_latest_event_block("Alienated"),
    )
    exit_request_deamon: EventDaemon = EventDaemon(
        trigger=exit_request_trigger,
        event=events.ExitRequest(),
        start_block=find_latest_event_block("ExitRequest"),
    )
    # pools_db_daemon: TimeDaemon = TimeDaemon(
    #     interval=21600, trigger=pools_db_trigger
    # )  # TODO: This will be removed after testing
    stake_daemon: BlockDaemon = BlockDaemon(trigger=stake_trigger, block_period=1)

    # Run the daemons
    # pools_db_daemon.run()
    id_initiated_daemon.run()
    deposit_deamon.run()
    delegation_daemon.run()
    fallback_operator_daemon.run()
    alienated_daemon.run()
    exit_request_deamon.run()
    stake_daemon.run()


def main():
    """Main function of the program.

    This function is called when the program is run.

    initializes the databases and sets up the daemons.
    """

    # make sure database is ok
    init_dbs()

    # Initialize and run the daemons
    try:
        setup_daemons()

    # pylint: disable-next=broad-exception-caught
    except Exception as e:
        # TODO: send mail.
        sys.exit(e)


if __name__ == "__main__":
    main()
