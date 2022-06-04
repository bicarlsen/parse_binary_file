from __future__ import annotations
import io
import struct
import typing
import collections
from dataclasses import dataclass, field

from .data_types import DataSize, DataFormat, EndianFormat
from .helpers import read_until
from .errors import AlreadyLoaded, ValuesDoNotMatch


@dataclass
class FieldDescription():
    """
    Represents a field description.
    """
    type: str = 'bytes'
    name: str = None
    value: typing.Any = None
    size: int = None
    terminator: typing.Any = None
    null_terminated: bool = False
    is_null: bool = False
    description: str = None
    elements: typing.Any = None  # used to describe specific fiel options for array like values

    # specific options
    str_encoding: str = 'utf-8'
    format: str = None  # format for unpacking bytes [For more info see: https://docs.python.org/3/library/struct.html#format-strings]

    def __post_init__(self):
        if self.size == 0:
            raise ValueError('`size` can not be 0')

        try:
            dsize = DataSize[self.type].value

        except KeyError:
            # type does not have known size, ignore
            pass

        else:
            # type has a known size
            if self.size is None:
                self.size = dsize

            if self.size != dsize:
                raise ValueError(f'`{self.type}` has a known size of {dsize} bytes, which conflicts with given size.')

        # check for termination condition
        if (
            (self.size is None)
            and (self.null_terminated is not True)
            and (self.terminator is None)
        ):
            if self.value is None:
                # no way to determine termination of field
                raise ValueError(f'Can not determine field termination for {self}')

            # infer size from value
            self.size = len(self.value)


@dataclass
class Field():
    """
    Represents a field.
    """
    desc: FieldDescription
    value: typing.Any = field(default = None, init = False)
    _size: int = None
    _data: bytes = None  # original data

    def __getattr__(self, name: str):
        if name == 'expected_value':
            return self.desc.value

        return getattr(self.desc, name)


    @property
    def size(self):
        if not self.null_terminated:
            return self.desc.size

        return self._size


    @property
    def data(self) -> bytes:
        """
        :returns bytes: Original data bytes.
        """
        return self._data


    @property
    def value_matches(self) -> bool:
        """
        :returns bool: If the loaded value equals the expected value from the description.
        """
        if self.value is None:
            raise RuntimeError('Value not set')

        return (self.value == self.desc.value)


    @staticmethod
    def from_dict(desc: typing.Dict) -> Field:
        return Field(FieldDescription(**desc))         


    def set_value(self, val: bytes, **options):
        """
        Set field value.

        :param val: Value to set.
        :param **options: 
        """
        self._data = val

        if self.type == 'bytes':
            self.value = val

        elif self.type == 'str':
            self.value = val.decode(self.str_encoding)

        else:
            fmt_byte_order = EndianFormat.little

            if (self.type[0] == '[') and (self.type[-1] == ']'):
                # list types
                dtype = self.type[1:-1]
                dsize = DataSize[dtype].value
                fmt_dtype = DataFormat[dtype].value
                format = f'{fmt_byte_order}{fmt_dtype}'

                if dtype == 'float':
                    nvals = len(val)/ dsize
                    if int(nvals) != nvals:
                        raise ValueError('Invalid byte size')

                    vals = [val[i:i+dsize] for i in nvals]
                    value = list(map(lambda v: struct.unpack(format, v), vals))
                    self.value = value

                else:
                    raise ValueError(f'Unknown format type `{self.type}')

            else:
                try:
                    fmt_dtype = DataFormat[self.type].value

                except KeyError:
                    raise ValueError(f'Unknown format type `{self.type}')

                fmt = f'{fmt_byte_order}{fmt_dtype}'
                self.value = struct.unpack(fmt, val)[0]

        # verify value



class Data():
    """
    Represents data from a file.
    """

    def __init__(
        self,
        fields: typing.List[Field],
        info: typing.Dict = None,
        defaults: typing.Dict = None
    ):
        # ensure only last field has size -1
        for f in fields[:-1]:
            l = f.size
            if l is None:
                continue

            if l < 0:
                raise ValueError(
                    'A field other than the last has size less than 0, indicating to read until the end of the data stream'
                )

        self._info = info
        self._fields = fields
        self._defaults = defaults
        self._loaded = False
        self._value = None

    def __getitem__(self, name: typing.Union[int, str]) -> Field:
        if isinstance(name, int):
            return self.fields[name]

        elif isinstance(name, str):
            for f in self.fields:
                if f.name == name:
                    return f

        else:
            raise TypeError('Invalid index type')


    @property
    def info(self) -> typing.Dict:
        return self._info


    @property
    def fields(self) -> typing.List[Field]:
        return self._fields


    @property
    def defaults(self) -> typing.Dict:
        return self._defaults


    @property   
    def is_loaded(self) -> bool:
        return self._loaded


    @property
    def value(self) -> typing.List[typing.Any]:
        """
        :returns list: List of values, if loaded,
            None otherwise.
        """
        if not self.is_loaded:
            return None

        if self._value is None:
            self._value = list(map(lambda field: field.value, self.fields))

        return self._value


    @property
    def named_field_values(self) -> typing.Dict[str, typing.Any]:
        """
        :returns dict: Dictionary of {name: value} pairs for named fields.
        """
        if not self.is_loaded:
            raise RuntimeError('Data not yet loaded')

        return {f.name: f.value for f in self.fields if f.name is not None}


    @staticmethod
    def from_dicts(desc: typing.List[dict], **kwargs) -> Data:
        """
        Instantiates a new `Data` using a list of dictionaries
        to describe its fields.

        :param desc: List of dictionaries describing the fields.
        :param **kwargs: Keyword arguments to pass to `Data()`.
        :returns: A new `Data` based on `desc`.
        """
        fields = [Field.from_dict(f) for f in desc]
        return Data(fields, **kwargs)


    def keys(self) -> collections.abc.KeysView:
        """
        :returns dict_keys: Keys of named fields.
        """
        return self.named_field_values.keys()


    def load(self, stream: io.RawIOBase):
        """
        Load data into fields from the provided stream
        """
        if self.is_loaded:
            raise AlreadyLoaded()

        for f in self.fields:
            # read stream
            if f.size is not None:
                if f.size > 0:
                    f.set_value(stream.read(f.size))

                elif f.size < 0:
                    f.set_value(stream.read())

            elif f.null_terminated:
                f.set_value(read_until(stream))

            elif f.terminator is not None:
                f.set_value(read_until(stream, f.terminator))

            else:
                raise ValueError(f'Could not determine how to read field. {f}')

        self._loaded = True
