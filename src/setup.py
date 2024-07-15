from typing import Callable

from src.globals import get_env
from src.common.loggable import Loggable
from src.globals.env import load_env
from src.globals.flags import collect_flags
from src.globals.config import apply_flags, init_config, preflight_checks
from src.globals.sdk import init_sdk
from src.globals.constants import init_constants
from src.globals import (
    set_config,
    set_env,
    set_sdk,
    set_flags,
    set_constants,
    set_logger,
)


def setup_globals(flag_collector: Callable = collect_flags):
    """Initializes the required components from the geonius script:
    - Loads environment variables from specified .env file
    - Applies the provided flags to be utilized in the config step
    - Creates a config dict from provided json
    - Configures the geodefi python sdk
    - Configures the constant parameters for ease of use

    Args:
        flag_collector (Callable): a fuunction that provides the will
        provide the provided flags with the help of argparse lib.
        Secondary scripts can have their own flags, then this should be speciifed.
        Otherwise, defaults to collect_flags.
    """
    set_flags(flag_collector())
    set_env(load_env())

    config = apply_flags(init_config())
    preflight_checks(config)
    set_config(config)

    set_logger(Loggable().logger)
    set_sdk(
        init_sdk(
            exec_api=get_env().EXECUTION_API,
            cons_api=get_env().CONSENSUS_API,
            priv_key=get_env().PRIVATE_KEY,
        )
    )
    set_constants(init_constants())
