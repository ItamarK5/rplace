from enum import IntEnum, auto


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