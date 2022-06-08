"""
Test Parser functionality.
"""
import pytest

from .parser import Parser
from .file_format import FileFormat


def test_parse_bytes():
    in_data = b'hello\xffthere\x00\x01\x00\x00\x00'
    info = {'byte_order': 'little'}
    defaults = {
        'str': {'terminator': b'\x00'}
    }

    ff = FileFormat.from_dicts([
        {'name': 'str1', 'type': 'str', 'terminator': b'\xff'},
        {'name': 'str2', 'type': 'str'},
        {'name': 'number', 'type': 'int'}
    ], info=info, defaults=defaults)

    parser = Parser(ff)
    data = parser.parse(in_data)

    assert data['str1'].value == 'hello'
    assert data['str2'].value == 'there'
    assert data[-1].value == 1
