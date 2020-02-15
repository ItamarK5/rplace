from painter.constants import MINUTES_COOLDOWN
from painter.models.user import User, Role

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


def role_icon(role: Role) -> str:
    return ROLE_ICON[role]


def role_title(role: Role) -> str:
    return ROLE_TITLE[role]


def draw_time(user: User) -> str:
    # https://stackoverflow.com/a/35643540
    if user.next_time == user.creation:
        return 'never'
    # else
    return user.next_time.strftime(
        '%y-%m-%d %a %H:%M:%S.%f'
    )


def is_admin(user: User) -> bool:
    return user.is_authenticated and user.role >= Role.admin
