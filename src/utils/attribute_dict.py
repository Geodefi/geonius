# -*- coding: utf-8 -*-


class AttributeDict(dict):
    """
    Inheriting the native dict class, AttributeDict allows dot notation on dict objects.

    As expected, it won't work for keys that start with an integer such as "3", "3x" etc.
    """

    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def convert_recursive(d: dict) -> AttributeDict:
    """
    Recursively converts intertwined dicts into AttributeDict

    Args:
        d (dict): A dict to recursively create an AttributeDict instance

    Returns:
        AttributeDict created from provided dict object
    """

    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = convert_recursive(v)

    return AttributeDict(**d)
