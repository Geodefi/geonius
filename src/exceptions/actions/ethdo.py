# -*- coding: utf-8 -*-

from ..custom_exception import CustomException


# TODO: catch after raise and send mail and continue
class EthdoError(CustomException):
    """Exception raised for errors in the ethdo call functions."""
