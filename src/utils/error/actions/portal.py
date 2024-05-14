from utils.error import CustomException


class CannotStakeError(CustomException):
    """Exception raised for errors in the call_stake function."""

    pass


class CallStakeError(CustomException):
    """Exception raised for errors in the call_stake function."""

    pass


class CallProposeError(CustomException):
    """Exception raised for errors in the call_proposeStake function."""

    pass
