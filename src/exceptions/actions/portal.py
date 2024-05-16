# -*- coding: utf-8 -*-

from ..custom_exception import CustomException


# TODO: catch after raise and send mail and continue
class CannotStakeError(CustomException):
    """Exception raised for errors in the canStake portal call issue."""


# TODO: daemon close
class CallFailedError(CustomException):
    """Exception raised for errors in the portal calls."""
