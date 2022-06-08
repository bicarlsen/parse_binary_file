from __future__ import annotations
import struct
import typing
from dataclasses import dataclass, field

from .data_types import (
    DataType,
    DataSize,
    DataFormat,
    EndianType,
    EndianFormat,
    is_numeric
)
from .errors import ValuesDoNotMatch
from .field_description import FieldDescription


@dataclass
class Field():
    """
    Represents a field.
    """
    desc: FieldDescription
    value: typing.Any | None = field(default=None, init=False)
    fields: typing.Tuple[Field] | None = None
    _size: int | None = None
    _data: bytes | None = None  # original data

    def __getattr__(self, name: str):
        """
        Attempts to retrieve properties from field description.
        """
        return getattr(self.desc, name)

    @property
    def size(self) -> int | None:
        return self._size

    @property
    def data(self) -> bytes | None:
        """
        :returns bytes: Original data bytes.
        """
        return self._data

    @property
    def expected_value(self):
        return self.desc.value

    @property
    def value_is_valid(self) -> bool:
        """
        :returns bool: If the loaded value equals the expected value from the description.
        """
        if self.value is None:
            raise RuntimeError('Value not set')

        if self.expected_value is None:
            # no expected value, vacuously true
            return True

        return (self.value == self.expected_value)

    @staticmethod
    def from_data(
        data: bytes,
        desc: FieldDescription
    ) -> Field:
        """
        Create a Field from data.

        :param data: The data to parse.
        :param desc: FieldDescription representing how the data should be parsed.
        :returns Field: A Field represnting the parsed data.
        """
        f = Field(desc)
        f.parse_data(data)
        return f

    def parse_data(self, val: bytes):
        """
        Set field value.

        :param val: Value to set.
        :param **options:
        """
        self._data = val

        if self.fields is not None:
            r_val = val[:]  # remaining values
            for f in self.fields:
                if f.size is not None:
                    if f.size == -1:
                        # consume remaining data
                        f_val = r_val
                        r_val = []

                    else:
                        try:
                            f_val = r_val[:f.size]

                        except IndexError:
                            raise IndexError('All data consumed before all fields terminated.')

                        r_val = r_val[f.size:]

                    f.set_value(f_val)

                else:
                    try:
                        f_stop = r_val.index(f.terminator) + len(f.terminator)

                    except ValueError:
                        raise ValueError('Terminator not found')

                    f_val = r_val[:f_stop]
                    r_val = r_val[f_stop:]

                    f.set_value(f_val)

            self.value = [f.value for f in self.fields]

        elif self.type == 'bytes':
            self.value = val

        elif self.type == 'str':
            if self.terminator is not None:
                # encode terminator if needed
                if not isinstance(self.terminator, bytes):
                    term = self.terminator.encode(self.format)

                else:
                    term = self.terminator

                if val[-len(self.terminator):] != term:
                    raise ValueError(
                        f'Value is not terminated by `{self.terminator}`'
                    )

                val = val[:-len(self.terminator)]

            try:
                self.value = val.decode(self.format)

            except UnicodeDecodeError as err:
                err.reason = f'{err.reason} for {self}'
                raise err

        else:
            fmt_byte_order = EndianFormat.LITTLE

            if (self.type[0] == '[') and (self.type[-1] == ']'):
                # list types
                dtype = self.type[1:-1]
                dsize = DataSize[dtype].value
                fmt_dtype = DataFormat[dtype].value
                format = f'{fmt_byte_order}{fmt_dtype}'

                if dtype == 'float':
                    nvals = len(val) / dsize
                    if int(nvals) != nvals:
                        raise ValueError('Invalid byte size')

                    vals = [val[i:i+dsize] for i in nvals]
                    value = list(map(lambda v: struct.unpack(format, v), vals))
                    self.value = value

                else:
                    raise ValueError(f'Unknown format type `{self.type}')

            else:
                try:
                    fmt_dtype = DataFormat[self.data_type.name].value

                except KeyError:
                    raise ValueError(f'Unknown format type `{self.type}')

                fmt = f'{fmt_byte_order.value}{fmt_dtype}'
                self.value = struct.unpack(fmt, val)[0]

        # @todo: validate value
        if self.expected_value is not None:
            exp_val = self.expected_value

            if (
                isinstance(exp_val, bytes)
                and isinstance(self.value, str)
            ):
                exp_val = exp_val.decode(self.format)

            if self.value != exp_val:
                raise ValueError(
                    f'Parsed value did not match expected for {self}'
                )