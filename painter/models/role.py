from enum import IntEnum, auto
from typing import Type, Any

from sqlalchemy import SmallInteger, TypeDecorator


class Role(IntEnum):
    # https://docs.python.org/3/library/enum.html
    banned = auto()
    common = auto()
    admin = auto()
    superuser = auto()

    @property
    def icon(self):
        return ROLE_ICON[self]

    @property
    def html_title(self):
        return ROLE_TITLE[self]


ROLE_ICON = {
    Role.admin: 'fa-user-shield',
    Role.common: 'fa-user',
    Role.banned: 'fa-ban',
    Role.superuser: 'fa-user-secret'
}

ROLE_TITLE = {
    Role.superuser: 'Superuser',
    Role.admin: 'Admin',
    Role.common: 'User',
    Role.banned: 'Banned'
}


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
