# -*- coding: utf-8 -*-

from ..custom_exception import CustomException


# TODO: sys exit in main
class PythonVersionException(CustomException):
    "Python version is not supported."
