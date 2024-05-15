# -*- coding: utf-8 -*-

from typing import Any
from geodefi.classes import Validator
from geodefi.globals import VALIDATOR_STATE

from src.globals import SDK, validators_table
from src.classes import Database, Trigger
from src.daemons import TimeDaemon
from src.helpers.db_validators import save_portal_state, save_local_state


class FinalizeExitTrigger(Trigger):
    """Trigger for the FINALIZE_EXIT. This time trigger is used to finalize the exit of a validator.
    It is triggered after the initial delay is passed. Initial delay is set according to exit epoch.
    It stops the daemon after the exit is finalized.

    Attributes:
        name (str): The name of the trigger to be used when logging etc. (value: FINALIZE_EXIT_TRIGGER)
        pubkey (str): The public key of the validator to finalize the exit
    """

    name: str = "FINALIZE_EXIT_TRIGGER"

    def __init__(self, pubkey: str) -> None:
        """Initializes a FinalizeExitTrigger object. The trigger will process the changes of the daemon after a loop.
        It is a callable object. It is used to process the changes of the daemon. It can only have 1 action.

        Args:
            pubkey (str): The public key of the validator to finalize the exit
        """

        Trigger.__init__(self, name=self.name, action=self.finalize_exit)
        self.pubkey: str = pubkey

    def finalize_exit(self, daemon: TimeDaemon, *args, **kwargs) -> None:
        """Finalizes the exit of the validator. Stops the daemon after the exit is finalized.
        Updates the database by setting the portal and local status to EXITED for the validator.

        Args:
            daemon (TimeDaemon): The daemon that triggers the action
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """

        # Check if the validator is in the exit state on the beacon chain
        val: Validator = SDK.portal.validator(self.pubkey)
        # TODO: check what the status is in the beacon chain
        if val.beacon_status != "exit":
            #  TODO: if it is too late from, after the initial delay is passed, we should raise an error
            # Too late => 1 week raise an error and cathch and send mail to operator and us
            return

        with Database() as db:
            db.execute(
                f"""
                    SELECT pool_id FROM {validators_table}
                    WHERE pubkey = {self.pubkey}
                """
            )
            row: Any = db.fetchone()
            if not row:
                # TODO: raise an error catch and exit deamon
                pass
        pool_id: int = int(row[0])
        SDK.portal.finalizeExit(pool_id, self.pubkey)

        # set db portal and local status to EXITED for validator
        save_portal_state(self.pubkey, VALIDATOR_STATE.EXITED)
        save_local_state(self.pubkey, VALIDATOR_STATE.EXITED)

        # stop the daemon since the validator is exited now and there is no need to check it anymore
        daemon.stop()
