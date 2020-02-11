from painter.models.user import User
from painter.constants import MINUTES_COOLDOWN


def draw_time(user: User) -> str:
    return (user.get_next_time()-MINUTES_COOLDOWN).strftime('%y-%m-%d %a %H:%M:%S')
