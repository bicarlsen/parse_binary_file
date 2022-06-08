import pytest
from .field import Field


# -------------
# --- Field ---
# -------------

def test_from_dict_basic():
    fd = {
        'size': 4,
        'name': 'test',
        'is_null': True
    }

    f = Field.from_dict(fd)

    assert f.size == fd['size']
    assert f.name == fd['name']
    assert f.is_null == fd['is_null']


def test_from_dict_with_subfields():
    dgc21 = {
        'name': 'grandchild 2-1',
        'size': 1
    }

    dgc22 = {
        'name': 'grandchild 2-2',
        'size': 4
    }

    dc1 = {
        'name': 'child 1',
        'size': 5
    }

    dc2 = {
        'name': 'child 2',
        'size': 5,
        'fields': [dgc21, dgc22]
    }

    fd = {
        'size': dc1['size'] + dc2['size'],
        'name': 'parent',
        'fields': [dc1, dc2]
    }

    f = Field.from_dict(fd)

    assert f.fields is not None
    c1 = f.fields[0]
    c2 = f.fields[1]

    assert c2.fields is not None
    gc21 = c2.fields[0]
    gc22 = c2.fields[1]

    assert c1.name == dc1['name']
    assert c2.name == dc2['name']
    assert gc21.name == dgc21['name']
    assert gc22.name == dgc22['name']


def test_expected_value():
    fd = {
        'value': 'hello',
    }

    f = Field.from_dict(fd)
    assert f.expected_value == fd['value']


def test_set_value_str_basic():
    fd = {
        'type': 'str',
        'options': {'null_terminated': True}
    }

    f = Field.from_dict(fd)

    data = b'hello\x00'
    f.set_value(data)
    assert f.value == 'hello'


def test_set_value_subfields():
    dc1 = {'type': 'int'}
    dc2 = {'type': 'str', 'options': {'null_terminated': True}}
    fd = {'fields': [dc1, dc2]}

    f = Field.from_dict(fd)
    data = b'\x01\x00\x00\x00hello\x00'

    f.set_value(data)
    c1 = f.fields[0]
    c2 = f.fields[1]

    assert c1.value == 1
    assert c2.value == 'hello'
    assert f.value == [1, 'hello']
