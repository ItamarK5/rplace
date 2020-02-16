from . import app
from painter.constants import MINUTES_COOLDOWN
from painter.models.user import User, Role
from typing import Optional, Union, List


@app.template_filter('draw_time')
def draw_time(user: User) -> str:
    # https://stackoverflow.com/a/35643540
    if user.next_time == user.creation:
        return 'never'
    # else
    return (user.next_time - MINUTES_COOLDOWN).strftime(
        '%y-%m-%d %a %H:%M:%S.%f'
    )


@app.template_filter('is_admin')
def is_admin(user: User) -> bool:
    return user.is_authenticated and user.role >= Role.admin


@app.template_filter('class_ftr')
def class_ftr(classes:Optional[Union[str, List]], comma: Optional[str]) -> str:
    if classes is None:
        return ''
    if isinstance(classes, str):
        classes = ' '.join(classes)
    # if comma
    if comma:
        return f'class="{comma}{classes}{comma}'
    return f" {classes}"
