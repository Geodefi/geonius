import pytest

from src.globals import hour_blocks


def test_all_constants():
    """
    test all constant vars for desired values.
    """
    assert hour_blocks == 300
