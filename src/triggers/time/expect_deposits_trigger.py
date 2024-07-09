# -*- coding: utf-8 -*-

from src.globals import SDK
from src.classes import Trigger
from src.daemons import TimeDaemon
from src.utils import multithread
from src.logger import log
from src.helpers import fill_validators_table


def ping_pubkey(pubkey: str) -> bool:
    try:
        SDK.beacon.beacon_states_validators_id(state_id="head", validator_id=pubkey)
        return True
    # pylint: disable=bare-except
    except:
        return False


class ExpectDepositsTrigger(Trigger):
    """_summary_

    Attributes:
        name (str): The name of the trigger to be used when logging etc. (value: EXPECT_DEPOSIT)
        pubkey (str): The public key of the validator to finalize the exit
    """

    name: str = "EXPECT_DEPOSITS"

    def __init__(self, pubkeys: list[str]) -> None:  # list : so waits many pubkeys.
        """_summary_

        Args:
            pubkey (str): _description_
        """
        Trigger.__init__(self, name=self.name, action=self.expect_deposits)
        self.pubkeys: str = pubkeys
        log.debug(f"{self.name} is initated for pubkey: {pubkeys}")

    def expect_deposits(self, daemon: TimeDaemon) -> None:
        """_summary_

        Args:
            daemon (TimeDaemon): _description_
        """
        all_pubkeys_exist: bool = all(multithread(ping_pubkey, self.pubkeys))
        if all_pubkeys_exist:
            fill_validators_table(self.pubkeys)
            daemon.stop()
        else:
            return
