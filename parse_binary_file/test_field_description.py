import pytest

from .field_description import FieldDescription
from .data_types import DataType
from .errors import TerminationConflict, IncompatibleProperties

# ------------------------
# --- FieldDescription ---
# ------------------------


def test_default_instantiation():
    """
    Check default instantiation.
    """
    fd = FieldDescription(size=4)

    assert fd.type == 'bytes'
    assert fd.name is None
    assert fd.size == 4
    assert fd.value is None
    assert fd.format is None
    assert fd.terminator is None
    assert fd.is_null is False
    assert fd.description is None
    assert fd.fields is None


def test_immuatble_properties():
    """
    Ensure properties are immutable.
    + type
    + value
    + size
    + format
    + terminator
    + is_null
    + fields
    + exec
    """
    fd = FieldDescription(size=4)

    with pytest.raises(AttributeError):
        fd.type = 'str'

    with pytest.raises(AttributeError):
        fd.value = 4

    with pytest.raises(AttributeError):
        fd.size = 4

    with pytest.raises(AttributeError):
        fd.format = None

    with pytest.raises(AttributeError):
        fd.terminator = b'\x00'

    with pytest.raises(AttributeError):
        fd.is_null = True

    with pytest.raises(AttributeError):
        fd.fields = None

    with pytest.raises(AttributeError):
        fd.exec = {}


def test_invalid_termination():
    with pytest.raises(ValueError):
        FieldDescription()


def test_invalid_type():
    with pytest.raises(ValueError):
        FieldDescription(type='invalid')


def test_invalid_size_for_known_type():
    with pytest.raises(IncompatibleProperties):
        FieldDescription(type='float', size=1)


def test_zero_size():
    with pytest.raises(ValueError):
        FieldDescription(size=0)


def test_size_set_from_value():
    val = '\x00\x00\x00\x00'
    fd = FieldDescription(value=val)
    assert fd.size == len(val)


def test_conflicting_size_and_value():
    with pytest.raises(IncompatibleProperties):
        FieldDescription(
            size='4',
            value=b'this it too long'
        )


def test_value_is_set_for_null_field():
    fd = FieldDescription(is_null=True, size=4)
    assert fd.value == b'\x00\x00\x00\x00'


def test_type_is_inferred_from_value():
    fd = FieldDescription(value='test')
    assert fd.type == 'str'


def test_data_type():
    """
    Ensure correct data types are assigned.
    """
    fd_bytes = FieldDescription(size=4)
    assert fd_bytes.data_type is DataType.BYTES

    fd_str = FieldDescription(type='str', size=4)
    assert fd_str.data_type is DataType.STRING

    fd_int = FieldDescription(type='int')
    assert fd_int.data_type is DataType.INT

    fd_long = FieldDescription(type='long')
    assert fd_long.data_type is DataType.LONG
