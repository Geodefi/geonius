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


# TODO: (later) Stop and throw error after x attempts: This should be fault tolerant. Rely on config.json
class ExpectDepositsTrigger(Trigger):
    """Trigger for the EXPECT_DEPOSITS. This time trigger waits until deposits for the
    multiple validators become processed on beaconchain. Works every 15 minutes.
    Validators should be proposed in a proposeStake call previously.
    Initial delay is proposed to be 12 hours after the call, which is usual. However, there is non
    if the script is rebooted. It stops the daemon after all the validators are recorded in db.

    Attributes:
        name (str): The name of the trigger to be used when logging etc. (value: EXPECT_DEPOSIT)
        __pubkeys (str): Internal list of validator pubkeys to be finalized when ALL exited.
        __keep_alive (str): TimeDaemon will not be shot down when pubkeys list is empty, if provided.
        Useful for event listeners.
    """

    name: str = "EXPECT_DEPOSITS"

    def __init__(self, pubkeys: list[str] = [], keep_alive: bool = False) -> None:
        Trigger.__init__(self, name=self.name, action=self.process_deposits)
        self.__pubkeys: str = pubkeys
        self.__keep_alive: bool = keep_alive
        get_logger().debug(f"{self.name} is initated.")

    def append(self, pubkeys: str, daemon: TimeDaemon = None):
        """Extends the internal pubkeys list provided list with 1 pubkey
            then immadiately processes the current list.

        Args:
            pubkey (str): pubkey to append into pubkeys list
            daemon (TimeDaemon): daemon to be stopped if the pubkey is empty
        """
        self.__pubkeys.append(pubkeys)
        self.process_deposits(daemon)

    def extend(self, pubkeys: str, daemon: TimeDaemon = None):
        """Extends the internal pubkeys list with provided list of more pubkeys
        then immadiately processes the current list.

        Args:
            pubkeys (list[str]): list of pubkeys to append into pubkeys list
            daemon (TimeDaemon): daemon to be stopped if the pubkey is empty
        """
        self.__pubkeys.extend(pubkeys)
        self.process_deposits(daemon)

    def process_deposits(self, daemon: TimeDaemon = None, *args, **kwargs) -> None:
        """Checks if any of the expected pubkeys are responding after the proposal deposit.
        Processes the ones that respond and keeps the ones that don't for the next iteration.

        Args:
            daemon (TimeDaemon): daemon to be stopped if the pubkey is empty
        """
        if self.__pubkeys:
            response_filter: bool = multithread(ping_pubkey, self.__pubkeys)

            responded = list()
            remaining = list()
            for pk, res in zip(self.__pubkeys, response_filter):
                if res:
                    remaining.append(pk)
                else:
                    remaining.append(pk)

            if len(responded) > 0:
                fill_validators_table(responded)

            if len(remaining) > 0:
                self.__pubkeys = remaining

        if not self.__keep_alive and daemon:
            daemon.stop()
