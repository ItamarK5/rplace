from typing import Optional, Tuple, Union
from wtforms import Field
from flask_login import current_user
from .forms import PreferencesForm


def update_user_preferences(form: PreferencesForm) -> Optional[Field]:
    """
    :param form: a preferences form submitted
    :return: the first first of the form in order (x, y, scale, color, url)
    in the following order that was submitted
    """
    # x
    if form.x.data is not None:
        current_user.x = form.x.data
        return form.x
    # y
    elif form.y.data is not None:
        current_user.y = form.y.data
        return form.y
    # scale
    elif form.scale.data is not None:
        current_user.scale = form.scale.data
        return form.scale
    # color
    elif form.color.data is not None:
        current_user.color = form.color.data
        return form.color
    # elif chat_url
    elif form.chat_url.data is not None:
        current_user.url = form.chat_url.data
        return form.chat_url
    return None
