"""
Name: enum_int
Contains the enum_int class support, a utility to save small integer enums (with 64 or less args) in sql
"""
from enum import IntEnum
from typing import Type, Any

from sqlalchemy import SmallInteger, TypeDecorator
from sqlalchemy.engine.default import DefaultDialect


class SmallEnum(TypeDecorator):
    """
    Enables passing in a Python enum and storing the enum's *value* in the db.
    The default would have stored the enum's *name* (ie the string).
    """

    @property
    def python_type(self):
        return int

    impl = SmallInteger

    def __init__(self, enum_type: Type[IntEnum], *args, **kwargs) -> None:
        """
        :param enum_type: the enum the column keeps
        :param args: anything for the init of the object
        :param kwargs: anything for the init of the object
        """
        super(SmallEnum, self).__init__(*args, **kwargs)
        self._enum_type = enum_type

    def process_bind_param(self, value: Any, dialect:DefaultDialect) -> int:
        """
        :param value: enum or integer
        :param dialect: dialect object
        :return:
        """
        # https://www.michaelcho.me/article/using-python-enums-in-sqlalchemy-models
        if isinstance(value, int):
            return value
        elif isinstance(value, self._enum_type):
            return value.value
        # else
        raise ValueError()

    def process_result_value(self, value: int, dialect:DefaultDialect) -> IntEnum:
        """
        :param value:
        :param dialect: some dialect object
        return
        :return: the enum represent the value
        convert sqlite integer to enum
        """
        try:
            return self._enum_type(value)
        except ValueError:
            raise ValueError('enum value isn\'t valid: %s' % value)
