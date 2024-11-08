from typing import Any
from src.globals import get_sdk, get_constants


def get_epoch_seconds_difference(target_epoch: int) -> int:
    """
    Calculate the difference in seconds between the current epoch and the target epoch.

    Args:
        target_epoch (int): The target epoch to calculate the difference from.

    Returns:
        int: The difference in seconds between the current epoch and the target epoch.
    """

    # calculate the delay for the daemon to run
    res: dict[str, Any] = get_sdk().beacon.beacon_headers_id("head")
    slots_per_epoch: int = 32
    slot_interval: int = int(get_constants().chain.interval)
    seconds_per_epoch: int = slots_per_epoch * slot_interval

    current_slot: int = int(res["header"]["message"]["slot"])
    current_epoch: int = current_slot // slots_per_epoch
    epoch_diff: int = current_epoch - target_epoch
    return epoch_diff * seconds_per_epoch
