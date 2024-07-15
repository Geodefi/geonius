# -*- coding: utf-8 -*-

from src.classes import Trigger
from src.daemons import TimeDaemon
from src.utils.thread import multithread
from src.database.validators import fill_validators_table
from src.globals import get_sdk, get_logger


def ping_pubkey(pubkey: str) -> bool:
    """Checks if a validator pubkey can be reached on beaconchain,
    if it exists without considering its status/state. Unusually, it just checks if the underlying call
    fires an error since it got 404 as a response instead of 200.

    Args:
        pubkey (str): public key of the validator to be pinged

    Returns:
        bool: True if the validator exists on the beaconchain, False if not.
    """
    try:
        get_sdk().beacon.beacon_states_validators_id(state_id="head", validator_id=pubkey)
        return True
    # pylint: disable=bare-except
    except:
        return False


# TODO: (now) like fill_pools_table, implement a function to fill the database on reboot with available data:  propose event daemon
# TODO: (later) Stop and throw error after x attempts: This should be fault tolerant. Rely on config.json
class ExpectDepositsTrigger(Trigger):
    """Trigger for the EXPECT_DEPOSITS. This time trigger waits until deposits for the
    multiple validators become processed on beaconchain. Works every 15 minutes.
    Validators should be proposed in a proposeStake call previously.
    Initial delay is proposed to be 12 hours after the call, which is usual. However, there is non
    if the script is rebooted. It stops the daemon after all the validators are recorded in db.

    Attributes:
        name (str): The name of the trigger to be used when logging etc. (value: EXPECT_DEPOSIT)
        pubkeys (str): The list of validator pubkeys to be finalized when ALL exited.
    """

    name: str = "EXPECT_DEPOSITS"

    def __init__(self, pubkeys: list[str]) -> None:  # list : so waits many pubkeys.
        """_summary_

        Args:
            pubkey (str): _description_
        """
        Trigger.__init__(self, name=self.name, action=self.expect_deposits)
        self.pubkeys: str = pubkeys
        get_logger().debug(f"{self.name} is initated for pubkey: {pubkeys}")

    def expect_deposits(self, daemon: TimeDaemon) -> None:
        """_summary_

        Args:
            daemon (TimeDaemon): _description_
        """
        response_filter: bool = multithread(ping_pubkey, self.pubkeys)

        responded = list()
        remaining = list()
        for pk, res in zip(self.pubkeys, response_filter):
            if res:
                remaining.append(pk)
            else:
                remaining.append(pk)

        if len(responded) > 0:
            fill_validators_table(self.pubkeys)

        if len(remaining) > 0:
            self.pubkeys = remaining
        else:
            daemon.stop()
        return
