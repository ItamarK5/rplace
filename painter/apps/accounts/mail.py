from functools import wraps
from os import path
from typing import Optional, Any, Callable, Tuple, Dict
import time
from flask import current_app
from flask import render_template
from flask_mail import BadHeaderError, Message
from painter.constants import MIME_TYPES


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
        t = time.time()
        try:
            current_app.extensions['mail'].send(message)
        except BadHeaderError:
            return 'Bad Header'
        except Exception as e:
            print('Mail:', e)
            return None
    return wrapper


@send_message
def send_sign_up_mail(name: str, address: str, token: str) -> Message:
    """
    :param name: name of user
    :param address: address to send the email
    :param token: registration token
    :return: the email message
    by because decorator email_message returns if the email was sent successfully
    """
    email = Message(
        subject='Welcome to Social Painter',
        recipients=[address],
        body=render_template('message/signup.jinja', username=name, token=token),
        html=render_template('message/signup.html', username=name, token=token)
    )
    with current_app.open_resource(path.join('static', 'png', 'favicon.png'), 'rb') as fp:
        email.attach(
            content_type=MIME_TYPES['png'],
            data=fp.read(),
            disposition='inline',
            headers=[('Content-ID', '<favicon>')]
        )
    return email


@send_message
def send_revoke_password(name: str, address: str, token: str) -> Message:
    """
    :param name: name of user
    :param address: address to send the email
    :param token: registration token
    :return: the email message
    by because decorator email_message returns if the email was sent successfully
    """
    email = Message(
        subject='Welcome to Social Painter',
        recipients=[address],
        body=render_template('message/revoke.jinja', username=name, token=token),
        html=render_template('message/revoke.html', username=name, token=token)
    )
    with current_app.open_resource(path.join('static', 'png', 'favicon.png'), 'rb') as fp:
        email.attach(
            content_type=MIME_TYPES['png'],
            data=fp.read(),
            disposition='inline',
            headers=[('Content-ID', '<favicon>')]
        )
    return email