from flask import current_app, abort
from flask_mail import BadHeaderError, Message
from flask_login import current_user
from flask_socketio import disconnect
from typing import TypeVar, Optional, Any, Callable, Tuple, Dict
from functools import wraps
from threading import Thread
from .constants import UserModel


def send_message(f: Callable[[Any], Message]) -> Callable[[Tuple[Any], Dict[str, Any]], Optional[str]]:
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


def run_async(name: Optional[str] = None) -> Callable:
    """
        run function asynchonize
    """
    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def wrapped(*args, **kwargs):
            if name:
                Thread(target=func, name=name, args=args, kwargs=kwargs).start()
            else:
                Thread(target=func, args=args, kwargs=kwargs).start()
        return wrapped
    return wrapper


def authenticated_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped
