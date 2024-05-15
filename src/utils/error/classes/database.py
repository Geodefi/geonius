from src.utils.error import CustomException


class DatabaseError(CustomException):
    """Exception raised for errors related with Database actions."""


class DatabaseMismatchError(DatabaseError):
    """Exception raised for errors related with Database mismatches."""
