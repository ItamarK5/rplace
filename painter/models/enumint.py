"""
Name: enumint
Contains the enumint class support, a utility to save small integer enums (with 64 or less args) in sql
"""
from enum import IntEnum
from typing import Type, Any

from sqlalchemy import SmallInteger, TypeDecorator


class SmallEnum(TypeDecorator):
    """
    Enables passing in a Python enum and storing the enum's *value* in the db.
    The default would have stored the enum's *name* (ie the string).
    """
    impl = SmallInteger

    def __init__(self, enum_type: Type[IntEnum], *args, **kwargs) -> None:
        super(SmallEnum, self).__init__(*args, **kwargs)
        self._enum_type = enum_type

    def process_bind_param(self, value: Any, dialect) -> int:
        # https://www.michaelcho.me/article/using-python-enums-in-sqlalchemy-models
        if isinstance(value, int):
            return value
        elif isinstance(value, self._enum_type):
            return value.value
        # else
        raise ValueError()

    def process_result_value(self, value, dialect) -> IntEnum:
        try:
            return self._enum_type(value)
        except ValueError:
            raise ValueError('user privilage value isnt valid: %s' % value)
