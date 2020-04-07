from enum import IntEnum, auto
from typing import Optional


class Role(IntEnum):
    # https://docs.python.org/3/library/enum.html
    common = auto()
    admin = auto()
    superuser = auto()

    @property
    def icon(self):
        return ROLE_ICON[self]

    @property
    def title(self):
        return ROLE_TITLE[self]

    @classmethod
    def has_member(cls, name:str) -> bool:
        return name in cls._member_names_

    @classmethod
    def get_member_or_none(cls, name: str) -> Optional['Role']:
        print(cls._member_map_, name)
        return cls._member_map_[name] if cls.has_member(name) else None


ROLE_ICON = {
    Role.admin: 'fa-user-shield',
    Role.common: 'fa-user',
    Role.superuser: 'fa-user-secret'
}

ROLE_TITLE = {
    Role.superuser: 'Superuser',
    Role.admin: 'Admin',
    Role.common: 'User',
}
