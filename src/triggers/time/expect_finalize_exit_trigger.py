# -*- coding: utf-8 -*-
from time import time
from src.classes import Trigger
from src.daemons import TimeDaemon
from src.globals import get_logger, get_constants
from src.utils.notify import send_email
from src.utils.thread import multithread
from src.utils.epoch_ts import get_epoch_seconds_difference
from src.helpers.portal import finalize_exit_on_portal_batch
from src.helpers.validator import fetch_validator_exiting_status


# TODO: (later) Stop and throw error after x attempts: This should be fault tolerant.
class ExpectFinalizeExitTrigger(Trigger):
    """Trigger for the EXPECT_PUBKEYS for the exitting process.
    A time trigger that waits for a list of pubkeys, and checks if any can be filtered
    according to the provided filter function. Works every 15 minutes.
    Initial delay can be provided.
    Can stop the daemon after all the validators are recorded in db, if keep_alive is False.

    Attributes:
        name (str): The name of the trigger to be used when logging etc. (value: EXPECT_DEPOSIT)
        __balance (int): When provided, the pubkeys will be filtered by the balance when detected.
        __status (str): When provided, the pubkeys will be filtered by the status when detected.
        __pubkeys (str): Internal list of validator pubkeys to be finalized when ALL exited.
        __keep_alive (str): TimeDaemon will not be shot down when pubkeys list is empty.
        Useful for event listeners.
    """

    name: str = "EXPECT_FINALIZE_EXIT"

    def __init__(
        self,
        pubkeys: list[str],
        append_timestamps: list[int],
        keep_alive: bool = False,
    ) -> None:
        Trigger.__init__(self, name=self.name, action=self.process_pubkeys)
        self.__append_timestamps: list[int] = append_timestamps
        self.__pubkeys: list[str] = pubkeys
        self.__keep_alive: bool = keep_alive
        get_logger().debug(f"{self.name} is initated.")

    def append(self, pubkey: str, daemon: TimeDaemon = None):
        """Extends the internal pubkeys list provided list with 1 pubkey
            then immadiately processes the current list.

        Args:
            pubkeys (list[str]): pubkey to append into pubkeys list
            daemon (TimeDaemon): daemon to be stopped if the pubkey is empty
        """
        self.__pubkeys.append(pubkey)
        self.__append_timestamps.append(int(time()))
        self.process_pubkeys(daemon)

    def extend(self, pubkeys: list[str], daemon: TimeDaemon = None):
        """Extends the internal pubkeys list with provided list of more pubkeys
        then immadiately processes the current list.

        Args:
            pubkeys (list[str]): list of pubkeys to append into pubkeys list
            daemon (TimeDaemon): daemon to be stopped if the pubkey is empty
        """
        self.__pubkeys.extend(pubkeys)
        self.__append_timestamps.extend([int(time())] * len(pubkeys))
        self.process_pubkeys(daemon)

    # pylint: disable-next=unused-argument
    def process_pubkeys(self, *args, daemon: TimeDaemon = None, **kwargs) -> None:
        """Checks if any of the expected pubkeys are responding after the proposal deposit.
        Processes the ones that respond and keeps the ones that don't for the next iteration.

        Args:
            daemon (TimeDaemon): daemon to be stopped if the pubkey is empty
        """
        if self.__pubkeys:

            statuses_epochs: list[(str, int)] = multithread(
                fetch_validator_exiting_status, self.__pubkeys
            )

            # get current timestamp
            current_timestamp: int = int(time())

            finalized = []
            remaining = []
            for pk, status_epoch, ts in zip(
                self.__pubkeys, statuses_epochs, self.__append_timestamps
            ):
                if status_epoch[0] == "withdrawal_done":
                    finalized.append(pk)

                else:
                    remaining.append(pk)
                    if current_timestamp - ts > 30 * get_constants().one_day:  # month
                        get_logger().warning(
                            f"Pubkey {pk} has not been finalized for a month. \
                                Current Status: {status_epoch[0]}, Epoch: {status_epoch[1]}"
                        )
                        send_email(
                            f"Pubkey {pk} has not been finalized for a month.",
                            f"Pubkey {pk} has not been finalized for a month. \
                                Current Status: {status_epoch[0]}, Epoch: {status_epoch[1]}",
                        )
                    if int(status_epoch[1]) == -1:  # week
                        if current_timestamp - ts > 7 * get_constants().one_day:  # week
                            get_logger().warning(
                                f"Pubkey {pk} has not been exitted on beacon chain for a week after exit call, \
                                    either call failed or there is a problem. Current Status: {status_epoch[0]}"
                            )
                            send_email(
                                f"Pubkey {pk} has not been finalized for a week after exit call.",
                                f"Pubkey {pk} has not been finalized for a week after exit call, \
                                    either call failed or there is a problem. Current Status: {status_epoch[0]}",
                            )
                        continue

                    time_difference: int = get_epoch_seconds_difference(int(status_epoch[1]))
                    if time_difference > 7 * get_constants().one_day:  # week
                        get_logger().warning(
                            f"Pubkey {pk} target epoch is too late for 7 days. \
                                Status: {status_epoch[0]}, Epoch: {status_epoch[1]}"
                        )
                        send_email(
                            f"Pubkey {pk} target epoch is too late for 7 days.",
                            f"Pubkey {pk} target epoch is too late for 7 days. \
                                Status: {status_epoch[0]}, Epoch: {status_epoch[1]}",
                        )

            if len(finalized) > 0:
                finalize_exit_on_portal_batch(finalized)

            self.__pubkeys: list[str] = remaining

        if not self.__keep_alive and daemon:
            daemon.stop()
