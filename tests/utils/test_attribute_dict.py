import pytest

from src.utils.attribute_dict import AttributeDict, convert_recursive

mydict: dict = {
    "will": [{"this": "convert"}],
    "3": "3",
    "str": "0",
    "up": 1,
    "down": {
        "x": 2,
        "down": {
            "x": 3,
            "down": {
                "x": 4,
            },
        },
    },
}


def test_dict_inherit():
    """
    test if convert_recursive works for intertwined dicts.
    """
    assert isinstance(convert_recursive(mydict), AttributeDict)


def test_convert_recursive():
    """
    test if convert_recursive works for intertwined dicts.
    """
    newdict = convert_recursive(mydict)
    assert newdict.will == [{"this": "convert"}]
    # assert newdict.3 == 3 # This won't work
    assert newdict.str == "0"
    assert newdict.up == 1
    assert newdict.down.x == 2
    assert newdict.down.down.x == 3
    assert newdict.down.down.down == AttributeDict({"x": 4})
    assert newdict.down.down.down.x == 4


def test_not_dict():
    """
    test if raises when not-a-dict is provided.
    """
    mystr = "mystr"
    assert not isinstance(mystr, AttributeDict)
    with pytest.raises(TypeError):
        convert_recursive(mystr)
