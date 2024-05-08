# -*- coding: utf-8 -*-


class AttributeDict(dict):
    """Inheriting the native dict class, AttributeDict allows dot notation on dict objects.
    As expected, it won't work for keys that start with an integer such as "3", "3x" etc.

    Example:
        d = AttributeDict({"a": 1, "b": {"c": 2, "d": 3}})
        d.a  # 1
        d.b.c  # 2

    Attributes:
        __slots__ (tuple): an empty tuple to prevent adding new attributes to the object.
    """

    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def convert_recursive(d: dict) -> AttributeDict:
    """Recursively converts intertwined dicts into AttributeDict objects. This is a helper function for CONFIG.

    Args:
        d (dict): A dict to recursively create an AttributeDict instance from.

    Returns:
        AttributeDict: An AttributeDict object with dot notation.
    """

    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = convert_recursive(v)

    return AttributeDict(**d)
