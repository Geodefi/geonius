from src.utils.error import CustomException


class SDKError(CustomException):
    """Exception raised for errors in the sdk initialization."""


class PrivateKeyMissingError(SDKError):
    """Exception raised for errors when the private key is missing."""
