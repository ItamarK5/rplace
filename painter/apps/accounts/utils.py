from __future__ import absolute_import

from functools import wraps
from typing import Any, Callable

from flask import redirect, url_for, flash, current_app
from flask_login import current_user


def anonymous_required(f: Callable) -> Callable[[Any], Any]:
    """
    :return: if the user is logined, redirects the user to another url
    decorator for a url, redirects the user if he is logined to home
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_anonymous:
            # get from configuration
            flash(current_app.config.get('APP_NON_LOGIN_MESSAGE', 'You have to logout to access this page'))
            # redirect to home page
            return redirect(url_for(current_app.config.get('APP_NON_LOGIN_ROUTE', 'auth.home')))
        # else, run function
        return f(*args, **kwargs)

    return wrapper
