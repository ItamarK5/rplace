"""
    File containing many html jinja related staff
    like filters and bootstrap
"""
from flask import Flask, url_for
from datetime import datetime
from typing import Optional, Union, List
from painter.models import User, Role
from painter.others.constants import COLORS
from painter.others.constants import COLOR_COOLDOWN


""" 
    Filters
"""


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
    :param classes: list of classes or just 1
    :param comma: a comma string ",' and etc.
    :return: the combined list of string as one
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


class CDNResource:
    def __init__(self, is_script: bool, src: str, **kwargs) -> None:
        self.is_script = is_script
        # get source
        self.__render_kwargs = (
            ('src' if self.is_script else 'href', src),
        )
        self.__render_kwargs += tuple(kwargs.items())

    def __render_attrs(self):
        return ' '.join([f'{pair[0]}="{pair[1]}"' for pair in self.__render_kwargs if pair[1] is not None])

    def render(self):
        if self.is_script:
            return f'<script {self.__render_attrs()} type="text/javascript">'
        # else
        return f'<link {self.__render_attrs()} type="text/css" rel="stylesheet">'


CDN_RESOURCES = {
    "underscore.js": CDNResource(
        True,
        "https://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.9.1/underscore-min.js",
        integrity="sha256-G7A4JrJjJlFqP0yamznwPjAApIKPkadeHfyIwiaa9e0=",
        crossorigin="anonymous"
    ),
    "bootstrap.css": CDNResource(
        False,
        "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css",
        integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh",
        crossorigin="anonymous"
    ),
    "font-awesome.js": CDNResource(
        False,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.11.2/css/fontawesome.min.css",
        integrity="sha256-/sdxenK1NDowSNuphgwjv8wSosSNZB0t5koXqd7XqOI=",
        crossorigin="anonymous"
    ),
    'popper.js': CDNResource(
        False,
        'https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js',
        'sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo',
        "anonymous"
    ),
    'bootstrap.js': CDNResource(
        False,
        'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js',
        'sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6',
        'anonymous'
    ),
    'jquery.js': CDNResource(
        False,
        "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js",
        integrity="sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo=",
        crossorigin="anonymous"
    ),
    'font-awesome.css': CDNResource(
        False,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.11.2/css/fontawesome.min.css",
        integrity="sha256",
        crossorigin="anonymous"
    ),
    'font-awesome-solid.css': CDNResource(
        False,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.11.2/css/solid.css",
        integrity="sha256-wMES50JHO82E/LjWWLWeCXXQahHeA0oemqGIfMkD5BI=",
        crossorigin="anonymous"
    ),
    'font-awesome-brands.css': CDNResource(
        False,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.11.2/css/brands.min.css",
        integrity="sha256-UZFVAO0Fn854ajzdWnJ2Oze6k1X4LNqE2RJPW3MBfq8=",
        crossorigin="anonymous"
    ),
    "sweetalert.js": CDNResource(
        True,
        "https://cdn.jsdelivr.net/npm/sweetalert2@9"
    )
}


def render_cdn_import(import_key: str) -> str:
    if import_key not in CDN_RESOURCES:
        raise RuntimeError("Cannot find key {}".format(import_key))
    # else
    return CDN_RESOURCES[import_key].render()


def render_import_static_style(file_key: str) -> str:
    # serve static path
    url = url_for('other.serve_static', static_file=file_key)
    if file_key.endswith(".js"):
        return f'<script src="{url}" type="text/javascript"></script>'
    # else
    return f'<link href="{url}" type="text/css">'


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
    flask_app.add_template_filter(render_cdn_import, "import_web")
    flask_app.add_template_filter(render_import_static_style, "import_static")
