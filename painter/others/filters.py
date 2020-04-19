"""
filters used in html rendering
"""
from __future__ import absolute_import
from typing import Optional, Union, List

from flask import Flask

from painter.models import User, Role
from painter.others.constants import COLORS
from painter.others.constants import COLOR_COOLDOWN
from datetime import datetime


def draw_time(user: User) -> str:
    """
    :param user: a user
    :return: the last time the user draw a pixel in the format displaed, if it never draw the value should be
    the creation date
    """
    # https://stackoverflow.com/a/35643540
    if user.next_time == user.creation_date:
        return 'never'
    # else
    return (user.next_time - COLOR_COOLDOWN).strftime(
        '%y-%m-%d %a %H:%M:%S'
    )


def is_admin(user: User) -> bool:
    """
    :param user: a user
    :return: returns if the user is admin
    """
    return user.is_authenticated and user.role >= Role.admin


def class_ftr(classes: Optional[Union[str, List]], comma: Optional[str] = None) -> str:
    """
    :param classes:
    :param comma:
    :return:
    """
    if classes is None:
        return ''
    if isinstance(classes, list):
        classes = ' '.join(classes)
    # if comma
    if comma:
        return f'class={comma}{classes}{comma}'
    return f" {classes}"


def color(color_idx: int) -> str:
    """
    :param color_idx: index of color in palette
    :return: the name of the color
    """
    return COLORS[color_idx]


def date(tm: datetime) -> str:
    """
    :param tm: datetime object, represent a time
    :return the datetime in format {first day of the week}, {date}
    https://www.programiz.com/python-programming/datetime/strftime
    """
    return tm.strftime('%a, %x')


def add_filters(flask_app: Flask) -> None:
    """
    :param flask_app: the application
    :return nothing
    adds all filters to the app
    """
    flask_app.add_template_filter(draw_time, 'draw_time')
    flask_app.add_template_filter(is_admin, 'is_admin')
    flask_app.add_template_filter(class_ftr, 'class_ftr')
    flask_app.add_template_filter(color, 'color')
    flask_app.add_template_filter(date, 'date')