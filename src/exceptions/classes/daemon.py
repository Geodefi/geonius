# -*- coding: utf-8 -*-

from ..custom_exception import CustomException


class DaemonError(CustomException):
    """Exception raised for errors in the Daemon class."""


class DaemonStoppedException(Exception):
    "Exception in thread background"
