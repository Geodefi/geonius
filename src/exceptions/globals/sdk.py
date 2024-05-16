# -*- coding: utf-8 -*-

from ..custom_exception import CustomException


# TODO: sys.exit at main
class SDKError(CustomException):
    """Exception raised for errors in the sdk initialization."""


# TODO: sys.exit at main
class MissingPrivateKeyError(SDKError):
    """Exception raised for errors when the private key is missing."""
