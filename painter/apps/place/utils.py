from typing import Optional

from flask_login import current_user
from wtforms import Field

from .forms import PreferencesForm


def update_user_preferences(form: PreferencesForm) -> Optional[Field]:
    """
    :param form: a preferences form submitted
    :return: the first first of the form in order (x, y, scale, color, url)
    in the following order that was submitted
    """
    # x
    if form.fav_x.data is not None:
        current_user.fav_x = form.fav_x.data
        return form.fav_x
    # y
    elif form.fav_y.data is not None:
        current_user.fav_y = form.fav_y.data
        return form.fav_y
    # scale
    elif form.fav_scale.data is not None:
        current_user.fav_scale = form.fav_scale.data
        return form.fav_scale
    # color
    elif form.fav_color.data is not None:
        current_user.fav_color = form.fav_color.data
        return form.fav_color
    # elif chat_url
    elif form.chat_url.data is not None:
        current_user.chat_url = form.chat_url.data
        return form.chat_url
    return None
