from __future__ import annotations
import struct
from typing import Union, Tuple, List, Dict, Any
from dataclasses import dataclass

from parse_binary_file.data_types import (
    DataFormat, DataType, EndianType, EndianFormat
)

from .field_description import FieldDescription


@dataclass
class FileFormat():
    """
    Describes the format of a file.
    """
    fields: List[FieldDescription]
    info: Union[Dict, None] = None

    def __post_init__(self):
        # @todo: Allow use of -1 size for subfields if parent has known termination.
        # ensure only last field has size -1
        invalid_sizes = tuple(map(
            lambda f: (f.size is not None) and (f.size < 0),
            self.fields
        ))

        if any(invalid_sizes[:-1]):
            raise ValueError(
                'A field other than the last has size less than 0, indicating to read until the end of the data stream'
            )

    def __getitem__(
        self,
        name: Union[int, str]
    ) -> Union[FieldDescription, Tuple[FieldDescription, ...]]:
        """
        Gets a field description by index or name.
        If by name and multiple fields with the same name exist,
        returns a tuple with them in order.

        :raises KeyError: If given an invalid field name.
        """
        if isinstance(name, bool):
            # required becaue `bool` is subclass of `int`
            raise TypeError('Invalid index type')

        if isinstance(name, int):
            return self.fields[name]

        elif isinstance(name, str):
            fields = []
            for f in self.fields:
                if f.name == name:
                    fields.append(f)

            if len(fields) == 0:
                raise KeyError(f'No field with name `{name}`')

            elif len(fields) == 1:
                return fields[0]

            else:
                return tuple(fields)

        else:
            raise TypeError('Invalid index type')

    @staticmethod
    def from_dicts(
        desc: Tuple[dict],
        info: Union[Dict[str, Any], None] = None,
        defaults: Union[Dict[str, Any], None] = None
    ) -> FileFormat:
        """
        Instantiates a new `Data` using a list of dictionaries
        to describe its fields.

        :param desc: List of dictionaries describing the fields.
        :param info: Dictionary of file info.
        :param defaults: Dictionary of default options to use
            for each field type.
        :returns FileFormat: A new `Data` based on `desc`.
        """
        term_fields = ['size', 'terminator', 'value']

        fields = []
        for f in desc:
            kind: str = f['type'] if ('type' in f) else 'bytes'
            if (defaults is not None) and (kind in defaults):
                d_opts = defaults[kind]

                # @todo: don't need to do in loop.
                # split options into termination fields and not
                term_opts = {
                    k: v for k, v in d_opts.items()
                    if k in term_fields
                }

                if len(term_opts) > 1:
                    raise ValueError(
                        f'Default termination conditions over specified for `{type}`, only one of `size`, `terminator`, or `value` may be set'
                    )

                d_opts = {
                    k: v for k, v in d_opts.items()
                    if k not in term_fields
                }

                # specify terminator
                nbr_terms = sum([  # number of termination fields specified
                    1 for t in term_fields
                    if (t in f) and (f[t] is not None)
                ])

                if nbr_terms == 0:
                    # only include termination defaults
                    # if no other termination conditions
                    # are sppecified
                    f = {**term_opts, **f}

                # include other defaults
                f = {**d_opts, **f}

            # set format
            if 'format' not in f:
                if kind in ['bytes', 'str']:
                    if (info is not None) and ('encoding' in info):
                        f['format'] = info['encoding']

                    else:
                        f['format'] = 'utf-8'

                else:
                    try:
                        d_type = DataType(kind)

                    except KeyError:
                        # unknown data type
                        raise ValueError(f'Unknown data type `{kind}`')

                    byte_order = (
                        info['byte_order']
                        if (info is not None) and ('byte_order' in info) else
                        'native'
                    )

                    try:
                        byte_order = EndianType(byte_order)

                    except KeyError:
                        # unknown byte order
                        raise ValueError(f'Unknown byte order `{byte_order}`')

                    b_fmt = EndianFormat[byte_order.name]
                    d_fmt = DataFormat[d_type.name]
                    fmt = f'{b_fmt}{d_fmt}'

                    f['format'] = fmt

            for tf in ['terminator', 'value']:
                if (tf in f) and (type(f[tf]) is not bytes):
                    if kind in ['bytes', 'str']:
                        f[tf] = bytes(f[tf], f['format'])

                    else:
                        f[tf] = struct.pack(f['format'], f[tf])

            fd = FieldDescription(**f)
            fields.append(fd)

        return FileFormat(fields, info=info)

    def keys(self) -> frozenset[str]:
        """
        :returns frozenset[str]: Keys of named fields.
        """
        names = {f.name for f in self.fields if f.name is not None}
        return frozenset(names)
