# -*- coding: utf-8 -*-

import sys
from src.globals.exceptions import PythonVersionException


def check_python_version() -> None:
    """Checks that the python version running is sufficient and exits if not."""

    if sys.version_info <= (3, 8) and sys.version_info >= (3, 10):
        raise PythonVersionException
        # pylint: disable=unreachable
        sys.exit()
