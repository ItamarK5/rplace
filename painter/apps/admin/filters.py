from painter.models.user import User, Role
from painter.constants import MINUTES_COOLDOWN
from typing import Dict, Any


def draw_time(user: User) -> str:
    # https://stackoverflow.com/a/35643540
    return (user.get_next_time()-MINUTES_COOLDOWN).strftime('%y-%m-%d %a %H:%M:%S.%f') if user.next_time != 0 else 'never'


def is_admin(user: User) -> bool:
    return user.is_authenticated and user.role >= Role.admin
