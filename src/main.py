# -*- coding: utf-8 -*-

from web3.contract.contract import ContractEvent

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
from src.globals import get_flags, get_sdk, get_constants, get_logger
from src.setup import setup


def init_dbs():
    """Initializes the databases if suited. Wipes out all data When reset flag is provided.

    This function is called at the beginning of the program to make sure the
    databases are up to date.
    """
    if get_flags().reset:
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


def setup_daemons():
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
    exit_request_daemon: EventDaemon = EventDaemon(
        trigger=exit_request_trigger,
        event=events.ExitRequest(),
    )
    stake_daemon: BlockDaemon = BlockDaemon(
        trigger=stake_trigger, block_period=0.5 * get_constants().hour_blocks
    )

    # Run the daemons
    id_initiated_daemon.run()
    deposit_daemon.run()
    delegation_daemon.run()
    stake_proposal_daemon.run()
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
        setup()
        init_dbs()
        setup_daemons()

    # pylint: disable-next=broad-exception-caught
    except Exception as e:
        try:
            get_logger().error(str(e))
            get_logger().error("Could not initiate geonius")
            get_logger().info("Exiting...")
        # pylint: disable-next=broad-exception-caught
        except Exception:
            print(str(e) + "\nCould not initiate geonius.\nExiting...")
        raise e


if __name__ == "__main__":
    main()
