import io
import logging
from typing import Union, Tuple, List

from .helpers import read_until
from .file_format import FileFormat
from .field_description import FieldDescription
from .field import Field
from .data import Data


class Parser():
    """
    Parses a file given a certain format.

    :raises TypeError: If the type of the stream is unknown.
    """
    def __init__(self, format: FileFormat):
        # set field options
        self.format = format

    def parse(self, stream: Union[io.IOBase, bytes]) -> Data:
        """
        Parse data into fields from the provided stream.
        """
        if isinstance(stream, bytes):
            return self._parse_bytes(stream)

        elif isinstance(stream, io.IOBase):
            return self._parse_io(stream)

        else:
            raise TypeError('Can not parse stream of given type')

    def _parse_io(self, stream: io.IOBase) -> Data:
        fields: List[Field] = []
        for fd in self.format.fields:
            if fd.size is not None:
                if fd.size > 0:
                    f = Field.from_data(stream.read(fd.size), fd)

                else:
                    # read till end of stream
                    f = Field.from_data(stream.read(), fd)

            elif fd.terminator is not None:
                f = Field.from_data(
                    read_until(stream, terminator=fd.terminator),
                    fd
                )

            else:
                raise ValueError(f'Could not determine how to read field. {fd}')

            fields.append(f)

        data = Data(tuple(fields))
        return data

    def _parse_bytes(self, stream: bytes) -> Data:
        fields: List[Field] = []
        for fd in self.format.fields:
            if fd.size is not None:
                if fd.size > 0:
                    f_data = stream[:fd.size]
                    stream = stream[fd.size:]
                    f = Field.from_data(f_data, fd)

                else:
                    # read till end of stream
                    f = Field.from_data(stream, fd)

            elif fd.terminator is not None:
                try:
                    t_index = stream.index(fd.terminator)

                except ValueError:
                    # terminator not found
                    # exhaust stream
                    f_data = stream
                    stream = b''

                else:
                    split = t_index + len(fd.terminator)
                    f_data = stream[:split]
                    stream = stream[split:]

                f = Field.from_data(f_data, fd)

            else:
                raise ValueError(f'Could not determine how to read field. {fd}')

            fields.append(f)

        data = Data(tuple(fields))
        return data
