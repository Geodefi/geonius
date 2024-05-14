from error import CustomException

from error.actions.ethdo import (
    GenerateDepositDataError,
    CreateWalletError,
    CreateAccountError,
    ExitValidatorError,
)

from error.actions.portal import CannotStakeError, CallStakeError, CallProposeError
