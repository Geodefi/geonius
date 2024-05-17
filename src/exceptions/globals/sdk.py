# -*- coding: utf-8 -*-

from ..custom_exception import CustomException


class SDKError(CustomException):
    """Exception raised for errors in the sdk initialization."""


class MissingPrivateKeyError(SDKError):
    """Exception raised for errors when the private key is missing."""
