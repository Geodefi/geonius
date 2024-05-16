# -*- coding: utf-8 -*-

from ..custom_exception import CustomException


class DatabaseError(CustomException):
    """Exception raised for errors related with Database actions."""


class DatabaseMismatchError(DatabaseError):
    """Exception raised for errors related with Database mismatches."""
