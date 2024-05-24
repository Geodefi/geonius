# -*- coding: utf-8 -*-
import sys
from web3.contract.contract import ContractEvent
from src.globals import SDK, FLAGS, hour_blocks
from src.daemons import BlockDaemon, EventDaemon
from src.triggers import (
    AlienatedTrigger,
    DelegationTrigger,
    FallbackOperatorTrigger,
    IdInitiatedTrigger,
    StakeTrigger,
    DepositTrigger,
    ExitRequestTrigger,
)
from src.utils import send_email
from src.helpers import (
    reinitialize_validators_table,
    reinitialize_pools_table,
    reinitialize_alienated_table,
    reinitialize_delegation_table,
    reinitialize_deposit_table,
    reinitialize_exit_request_table,
    reinitialize_fallback_operator_table,
    reinitialize_id_initiated_table,
)


def init_dbs():
    """Initializes the databases and fills them with the current data.

    This function is called at the beginning of the program to make sure the
    databases are up to date.
    """
    if FLAGS.reset:
        reinitialize_validators_table()
        reinitialize_pools_table()
        reinitialize_alienated_table()
        reinitialize_delegation_table()
        reinitialize_deposit_table()
        reinitialize_exit_request_table()
        reinitialize_fallback_operator_table()
        reinitialize_id_initiated_table()
        reinitialize_pools_table()

    # fill_pools_table(get_all_pool_ids()) # These are not needed, utilize daemons
    # fill_validators_table(get_all_owned_pubkeys()) # These are not needed, utilize daemons


def setup_daemons():
    """Initializes and runs the daemons for the triggers.

    This function is called at the beginning of the program to make sure the
    daemons are running.
    """
    events: ContractEvent = SDK.portal.contract.events
    # Triggers

    id_initiated_trigger: IdInitiatedTrigger = IdInitiatedTrigger()
    deposit_trigger: DepositTrigger = DepositTrigger()
    delegation_trigger: DelegationTrigger = DelegationTrigger()
    fallback_operator_trigger: FallbackOperatorTrigger = FallbackOperatorTrigger()
    alienated_trigger: AlienatedTrigger = AlienatedTrigger()
    exit_request_trigger: ExitRequestTrigger = ExitRequestTrigger()
    stake_trigger: StakeTrigger = StakeTrigger()

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
    fallback_operator_daemon: EventDaemon = EventDaemon(
        trigger=fallback_operator_trigger,
        event=events.FallbackOperator(),
    )
    alienated_daemon: EventDaemon = EventDaemon(
        trigger=alienated_trigger,
        event=events.Alienated(),
    )
    exit_request_daemon: EventDaemon = EventDaemon(
        trigger=exit_request_trigger,
        event=events.ExitRequest(),
    )
    stake_daemon: BlockDaemon = BlockDaemon(trigger=stake_trigger, block_period=0.5 * hour_blocks)

    # Run the daemons
    id_initiated_daemon.run()
    deposit_daemon.run()
    delegation_daemon.run()
    fallback_operator_daemon.run()
    alienated_daemon.run()
    exit_request_daemon.run()
    stake_daemon.run()


def main():
    """Main function of the program.

    This function is called when the program is run.

    initializes the databases and sets up the daemons.
    """

    try:
        init_dbs()
        setup_daemons()

    # pylint: disable-next=broad-exception-caught
    except Exception as e:
        send_email(e.__class__.__name__, str(e), [("<log_file_path>", "<file_name>.log")])
        sys.exit(e)


if __name__ == "__main__":
    main()
