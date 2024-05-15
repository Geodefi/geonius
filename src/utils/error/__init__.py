from error import CustomException

from error.actions.ethdo import EthdoError
from error.actions.portal import CannotStakeError, CallFailedError

from error.classes.daemon import DaemonError
from error.classes.database import DatabaseError, DatabaseMismatchError
from error.classes.trigger import TriggerError

from error.globals.sdk import SDKError, PrivateKeyMissingError
