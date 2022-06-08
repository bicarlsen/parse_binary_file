"""
Data type definitions.
"""
from enum import Enum


class DataType(Enum):
    """
    Names of data types.
    """
    BYTES = 'bytes'
    STRING = 'str'

    CHAR = 'char'
    BOOL = 'bool'
    SHORT = 'short'
    U_SHORT = 'u_short'
    INT = 'int'
    U_INT = 'u_int'
    DOUBLE = 'double'
    LONG = 'long'
    U_LONG = 'u_long'
    FLOAT = 'float'
    LONG_LONG = 'long_long'
    U_LONG_LONG = 'u_long_long'


class DataSize(Enum):
    """
    Sizes of data types.
    [For more information see:
    https://docs.python.org/3/library/struct.html#format-characters]
    """
    CHAR = 1
    BOOL = 1
    SHORT = 2
    U_SHORT = 2
    INT = 4
    U_INT = 4
    FLOAT = 4
    DOUBLE = 8
    LONG = 4
    U_LONG = 4
    LONG_LONG = 8
    U_LONG_LONG = 8


class DataFormat(Enum):
    """
    Format characters for data types.
    [For more information see:
    https://docs.python.org/3/library/struct.html#format-characters]
    """
    CHAR = 'c'
    BOOL = '?'
    SHORT = 'h'
    U_SHORT = 'H'
    INT = 'i'
    U_INT = 'I'
    FLOAT = 'f'
    DOUBLE = 'd'
    LONG = 'l'
    U_LONG = 'L'
    LONG_LONG = 'q'
    U_LONG_LONG = 'Q'


class EndianType(Enum):
    NATIVE = 'native'
    LITTLE = 'little'
    BIG = 'big'


class EndianFormat(Enum):
    NATIVE = '='
    LITTLE = '<'
    BIG = '>'


NUMERIC_DATA_TYPES = {
    DataType.SHORT, DataType.U_SHORT,
    DataType.INT, DataType.U_INT,
    DataType.FLOAT, DataType.DOUBLE,
    DataType.LONG, DataType.LONG_LONG,
    DataType.U_LONG_LONG,
}


def is_numeric(data: DataType) -> bool:
    """
    :returns bool: Whether the passed data type is of a numeric value.
    """
    return (data in NUMERIC_DATA_TYPES)
