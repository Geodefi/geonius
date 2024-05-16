# -*- coding: utf-8 -*-
from ..custom_exception import CustomException


# TODO: sys.exit at main
class ConfigurationError(CustomException):
    "An error occurred during configuration."
