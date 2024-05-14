from utils.error import CustomException


# Define custom exception classes inheriting from SimpleException
class GenerateDepositDataError(CustomException):
    """Exception raised for errors in the generate_deposit_data function."""

    pass


class CreateWalletError(CustomException):
    """Exception raised for errors in the create_wallet function."""

    pass


class CreateAccountError(CustomException):
    """Exception raised for errors in the create_account function."""

    pass


class ExitValidatorError(CustomException):
    """Exception raised for errors in the exit_validator function."""

    pass
