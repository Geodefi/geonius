# -*- coding: utf-8 -*-

from ..custom_exception import CustomException


# TODO: sys.exit at main
class DaemonError(CustomException):
    """Exception raised for errors in the Daemon class."""


# TODO: sys.exit at main
class DaemonStoppedException(DaemonError):
    "Exception in thread background"
