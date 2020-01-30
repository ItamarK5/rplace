from flask import current_app
from flask_mail import BadHeaderError, Message
from flask_login import login_required, current_user
from flask_socketio import disconnect
from typing import TypeVar, Optional, Any, Callable, Tuple, Dict
from functools import wraps
from threading import Thread

Decorated = TypeVar('Decorated')


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


def run_async(name: str) -> Callable:
    """
        run function asynchonize
    """
    def wrapper_args(func: Decorated) -> Decorated:
        @wraps(func)
        def wrapper(*args, **kwargs):
            Thread(target=func, name=name, args=args, kwargs=kwargs).start()
        return wrapper
    return wrapper_args


def authenticated_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped
