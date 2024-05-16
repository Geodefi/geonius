# -*- coding: utf-8 -*-

from ..custom_exception import CustomException


# TODO: sys.exit at main
class DatabaseError(CustomException):
    """Exception raised for errors related with Database actions."""


# TODO: sys.exit at main
class DatabaseMismatchError(DatabaseError):
    """Exception raised for errors related with Database mismatches."""
