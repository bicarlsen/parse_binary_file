"""
Test FileFormat functionality.
"""
import pytest

from .file_format import FileFormat
from .field_description import FieldDescription


def test_negative_size_in_last_position_does_not_raise_error():
    FileFormat([
        FieldDescription(size=4),
        FieldDescription(size=-1)
    ])


def test_negative_size_in_not_last_position_raises_value_error():
    with pytest.raises(ValueError):
        FileFormat([
            FieldDescription(size=-1),
            FieldDescription(size=4)
        ])


def test_get_fields_by_name_works():
    ff = FileFormat([
        FieldDescription(name='f1', size=1),
        FieldDescription(name='f2', size=2)
    ])

    assert ff['f1'].size == 1
    assert ff['f2'].size == 2


def test_get_fields_by_index_works():
    ff = FileFormat([
        FieldDescription(name='f1', size=1),
        FieldDescription(name='f2', size=2)
    ])

    assert ff[0].name == 'f1'
    assert ff[-1].name == 'f2'


def test_get_invalid_field_name_raises_key_error():
    ff = FileFormat([
        FieldDescription(name='f1', size=1),
        FieldDescription(name='f2', size=2)
    ])

    with pytest.raises(KeyError):
        ff['invalid']


def test_get_invalid_field_type_raises_type_error():
    ff = FileFormat([
        FieldDescription(name='f1', size=1),
        FieldDescription(name='f2', size=2)
    ])

    with pytest.raises(TypeError):
        print(ff[True])


def test_from_dicts():
    dicts = [
        {'name': 'f1', 'size': 4},
        {'name': 'f2', 'size': 4}
    ]

    ff = FileFormat.from_dicts(dicts)
    assert ff[0].name == 'f1'
    assert ff[1].name == 'f2'


def test_field_descriptions_receive_default_options():
    dicts = [
        {'name': 'f_bytes', 'size': 4},
        {'name': 'f_str', 'type': 'str', 'options': {'null_terminated': True}}
    ]

    options = {
            'bytes': {'byte_order': 'little'},
            'str': {'encoding': 'utf-16'}
    }

    ff = FileFormat.from_dicts(dicts, default_options=options)
    assert ff['f_bytes'].options['byte_order'] == 'little'
    assert ff['f_str'].options['null_terminated'] is True
    assert ff['f_str'].options['encoding'] == 'utf-16'


def test_keys():
    ff = FileFormat([
        FieldDescription(name='f1', size=1),
        FieldDescription(name='f2', size=2)
    ])

    keys = ff.keys()
    assert ('f1' in keys) and ('f2' in keys)
