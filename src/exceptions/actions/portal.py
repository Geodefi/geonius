from src.utils.error import CustomException


class CannotStakeError(CustomException):
    """Exception raised for errors in the canStake portal call issue."""


class CallFailedError(CustomException):
    """Exception raised for errors in the portal calls."""
