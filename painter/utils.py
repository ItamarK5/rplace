from functools import wraps
from typing import Optional, Any, Callable, Tuple, Dict
from flask import current_app, abort
from flask_login import current_user, fresh_login_required
from flask_mail import BadHeaderError, Message
from .models.role import Role

def send_message(f: Callable[[Any], Message]) -> Callable[[Tuple[Any], Dict[str, Any]], Optional[str]]:
    """
    :param f: a function that return a Message object
    :return: decorates the function
    """

    @wraps(f)
    def wrapper(*args, **kwargs) -> Optional[str]:
        if not current_app.config.get('MAIL_SUPPRESS_SEND', True):
            return None
        message = f(*args, **kwargs)
        try:
            current_app.extensions['mail'].send(message)
        except BadHeaderError:
            return 'Bad Header'
        except Exception as e:
            print('Mail:', e)
            return None

    return wrapper


def admin_only(f: Callable) -> Callable:
    """
    :param f: decorator, which decorates a view, make it admin only used
    :return: a route that aborts 404 non-admin users that enter, all actions of admin must be with refreshed login
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.is_authenticated and current_user.has_required_status(Role.admin):
            # decorated by flesh_login_required, so that it user isnt refreshed and prevent seeing the site
            return fresh_login_required(f)(*args, **kwargs)
        # else
        abort(404)
    return wrapped
