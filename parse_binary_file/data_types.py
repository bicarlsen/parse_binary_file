from enum import Enum


class DataSize(Enum):
    """
    Sizes of data types.
    [For more information,
    see: https://docs.python.org/3/library/struct.html#format-characters]
    """
    char = 1
    short = 2
    int = 4
    unisigned_int = 4
    float = 4
    double = 8
    long = 4
    unsigned_long = 4


class DataFormat(Enum):
    char = 'c'
    short = 'h'
    int = 'i'
    unisigned_int = 'I'
    float = 'f'
    double = 'd'
    long = 'l'
    unsigned_long = 'L'


class EndianFormat:
    little = '<'
    big = '>'
