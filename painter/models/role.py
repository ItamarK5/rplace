
from enum import IntEnum, auto
from typing import Optional


class Role(IntEnum):
    # https://docs.python.org/3/library/enum.html
    common = auto()  # role of a common user
    admin = auto()  # role of an admin, a user who has some administeration abilites on use
    superuser = auto()  # a user who controls the admins

    @property
    def icon(self):
        """
        :return: the icon of the roles
        """
        return _ROLE_ICON[self]

    @property
    def title(self) -> str:
        """
        :return: string the equivalent to the title of the Role
        """
        return _ROLE_TITLE[self]

    @classmethod
    def has_member(cls, name: str) -> bool:
        """
        :param name: some string
        :return: if the string represent a name of a role
        """
        return name in cls._member_names_

    @classmethod
    def get_member_or_none(cls, name: str) -> Optional['Role']:
        """
        :param name: name of a role
        :return: the role that matches the name, otherwise None
        """
        return cls._member_map_[name] if cls.has_member(name) else None


"""
Dictionaries for maps
"""

_ROLE_ICON = {
    Role.admin: 'fa-user-shield',
    Role.common: 'fa-user',
    Role.superuser: 'fa-user-secret'
}

_ROLE_TITLE = {
    Role.superuser: 'Superuser',
    Role.admin: 'Admin',
    Role.common: 'User',
}

__all__ = ['Role']
