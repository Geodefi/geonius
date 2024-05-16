# -*- coding: utf-8 -*-

from ..custom_exception import CustomException


# TODO: daemon close
class BeaconStateMismatchError(CustomException):
    """Exception raised for errors related with Beacon State mismatches."""
