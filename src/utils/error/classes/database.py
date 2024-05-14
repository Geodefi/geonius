from utils.error import CustomException


class DatabaseError(CustomException):
    """Exception raised for errors related with Database actions."""

    pass


class DatabaseMismatchError(CustomException):
    """Exception raised for errors related with Database mismatches."""

    pass
