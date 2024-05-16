# -*- coding: utf-8 -*-
from ..custom_exception import CustomException


class MissingConfigException(CustomException):
    "Config file is missing"
