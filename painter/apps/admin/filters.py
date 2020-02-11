from painter.models.user import User
from painter.constants import MINUTES_COOLDOWN


def draw_time(user: User) -> str:
    # https://stackoverflow.com/a/35643540
    return (user.get_next_time()-MINUTES_COOLDOWN).strftime('%y-%m-%d %a %H:%M:%S.%f') if user.next_time != 0 else 'never'