from flask import current_app
from flask_mail import BadHeaderError, Message
from typing import TypeVar, Optional, Callable
from functools import wraps
from threading import Thread

Decorated = TypeVar('Decorated')


def send_message(f: Decorated) -> Decorated:
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


def run_async(f: Decorated, name: str) -> Decorated:
    """
    Might be used in the future
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        Thread(target=f, args=args, kwargs=kwargs).start()
    return wrapper
