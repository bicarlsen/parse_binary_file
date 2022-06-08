from typing import Union, Iterable, Dict, Tuple, Any
from dataclasses import dataclass, field

from .field_description import FieldDescription
from .file_format import FileFormat
from .field import Field


@dataclass
class Data():
    """
    Represents data from a file.
    """
    _fields: Tuple[Field]
    _value: Any = field(default=None, init=False)
    _is_loaded: bool = False

    def __init__(
        self,
        fields: Tuple[Field],
    ):
        self._fields = fields
        self._is_loaded = False

    def __getitem__(
        self,
        name: Union[int, str]
    ) -> Union[Field, Tuple[Field, ...]]:
        """
        Gets a field by index or name.
        If by name and multiple fields with the same name exist,
        returns a tuple with them in order.

        :raises KeyError: If given an invalid field name.
        """
        if isinstance(name, int):
            return self.fields[name]

        if isinstance(name, str):
            fields = []
            for f in self.fields:
                if f.name == name:
                    fields.append(f)

            if len(fields) == 0:
                raise KeyError(f'No field with name `{name}`')

            if len(fields) == 1:
                return fields[0]

            else:
                return tuple(fields)

        else:
            raise TypeError('Invalid index type')

    @property
    def is_loaded(self) -> bool:
        """
        :returns bool: If data has been loaded.
        """
        return self._is_loaded

    @property
    def fields(self) -> Tuple[Field]:
        """
        :returns tuple[Field]: Tuple of fields.
        """
        return self._fields

    @property
    def value(self) -> Tuple[Any]:
        """
        :returns tuple: Tuple of values.
        """
        if self._value is None:
            self._value = tuple(map(lambda f: f.value, self.fields))

        return self._value

    @property
    def named_field_values(self) -> Dict[str, Any]:
        """
        :returns dict: Dictionary of {name: value} pairs for named fields.
            If multiple fields with the same name exist
            the value is a tuple with their values, in order.
        """
        vals = {}
        for f in self.fields:
            if f.name is None:
                continue

            if f.name in vals:
                if isinstance(vals[f.name], tuple):
                    vals[f.name] = (*vals[f.name], f.value)

                else:
                    vals[f.name] = (vals[f.name], f.value)

            else:
                vals[f.name] = f.value

        return vals