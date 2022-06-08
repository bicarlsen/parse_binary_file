from __future__ import annotations
from typing import Union, Any, Iterable, Tuple, List, Dict, Callable
from dataclasses import dataclass, field

from .data_types import (
    DataType,
    DataSize,
    DataFormat,
    EndianType,
    EndianFormat,
    is_numeric
)
from .errors import IncompatibleProperties


PossibleException = Union[Exception, None]


@dataclass
class FieldDescription():
    """
    Represents a field description.

    Properties:
    + **type:** Type of the field. [Default: 'bytes']
    + **name:** Name of the field.
    + **size:** Size of the field in bytes.
    + **format:** Parsing format for the data. Type dependent.
    + **terminator:** Termination string.
    + **is_null:** Indicates all bytes should be null.
    + **description:** Description of the field.
    + **fields:** Subfields.
    + **exec:** Pre and post execution hooks.
    """
    _data_type: DataType = field(init=False)
    _type: Union[str, None] = field(init=False, default=None)
    _value: Any = field(init=False, default=None)
    _size: Union[int, None] = field(init=False, default=None)
    _format: Union[str, None] = field(init=False, default=None)
    _terminator: Any = field(init=False, default=None)
    _is_null: bool = field(init=False, default=False)
    _fields: Union[Iterable[FieldDescription], None] = field(init=False, default=None)
    _exec: Union[Dict[str, Callable], None] = field(init=False, default=None)

    name: Union[str, None] = None
    description: Union[str, None] = None

    def __init__(
        self,
        type: Union[str, None] = None,
        value: Any = None,
        size: Union[int, None] = None,
        format: Union[str, None] = None,
        terminator: Any = None,
        is_null: bool = False,
        fields: Union[Iterable[FieldDescription], None] = None,
        exec: Union[Dict[str, Callable], None] = None,
        name: Union[str, None] = None,
        description: Union[str, None] = None
    ):
        """

        """
        self._type = type
        self._value = value
        self._size = size
        self._format = format
        self._terminator = terminator
        self._is_null = is_null
        self._fields = fields
        self._exec = exec
        self.name = name
        self.description = description

        self.__post_init__()

    def __post_init__(self):
        # @todo: handle different sizes of numeric types.
        # @todo: validate `type` and `value` are compatible.
        # set type if needed
        if self.size == 0:
            raise ValueError('`size` can not be 0')

        if self.type is None:
            # default to `bytes`
            self._type = 'bytes'

            if self.value is not None:
                # infer from value
                kind = type(self.value).__name__
                if kind == 'str':
                    # @todo: differentiate between `str` and `bytes`
                    kind = 'bytes'

                self._type = kind

        # get data type
        try:
            self._data_type = DataType(self.type)

        except ValueError:
            raise ValueError(f'Invalid data type {self.type}')

        # get size of type if known
        try:
            dsize = DataSize[self.data_type.name].value

        except KeyError:
            # type does not have known size
            # check value and size are compatible
            if (self.value is not None) and (self.size is not None):
                if len(self.value) != self.size:
                    raise IncompatibleProperties(
                        'Size of `value` does not match `size`',
                        'size', 'value'
                    )

        else:
            # type has a known size
            if self.size is None:
                self._size = dsize

            if self.size != dsize:
                raise IncompatibleProperties(
                    f'`{self.type}` has a known size of {dsize} bytes, which conflicts with given size.',
                    'type', 'size'
                )
        
        # validate terminators
        # only one of `size`, `terminator`, or `value` may be provided.
        # @todo: If `fields` is provided make sure it coheres.
        nbr_terms = sum([
            1 for t in [self.size, self.terminator, self.value]
            if t is not None
        ])

        if nbr_terms == 0:
            raise ValueError(
                'Termination condition is under specified. Must provide one of `size`, `terminator`, or `value`'
            )

        if nbr_terms > 1:
            raise ValueError(
                'Terminators are over specified. Only one of `size`, `terminator`, or `value` may be specified.'
            )

        # check for termination condition
        if (
            (self.size is None)
            and (self.terminator is None)
            and (self.fields is None)
        ):
            if self.value is None:
                # no way to determine termination of field
                raise ValueError(f'Can not determine field termination for {self}')

            # infer size from value
            self._size = len(self.value)

        # set type specific options, if not declared
        if self.type == 'str':
            if (
                (self.terminator is None)
                and (self.size is None)
            ):
                self._terminator = b'\x00'

            if self.format is None:
                self._format = 'utf-8'

        # attempt to get data format
        if self.format is None:
            try:
                format = DataFormat[self.data_type.name]  # format for unpacking bytes [For more info see: https://docs.python.org/3/library/struct.html#format-strings]

            except KeyError:
                # data type does not have a format string
                pass

            else:
                if self.format is None:
                    self._format = format.value

        # if is_null, set missing values
        if self.is_null and (self.value is None):
            if self.size is None:
                raise ValueError('Can not determine termination')

            self._value = b'\x00' * self.size

    @property
    def data_type(self) -> DataType:
        return self._data_type

    @property
    def type(self) -> Union[str, None]:
        return self._type

    @property
    def value(self) -> Any:
        return self._value

    @property
    def size(self) -> Union[int, None]:
        return self._size

    @property
    def format(self) -> Union[str, None]:
        return self._format

    @property
    def terminator(self) -> Any:
        return self._terminator

    @property
    def is_null(self) -> bool:
        return self._is_null

    @property
    def fields(self) -> Union[Tuple[FieldDescription], None]:
        return (
            None
            if self._fields is None else
            tuple(self._fields)
        )

    @property
    def exec(self) -> Union[Dict[str, Callable], None]:
        return self._exec
