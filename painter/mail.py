from flask import render_template
from functools import wraps
from typing import Optional
import flask_mail
from typing import Callable, TypeVar
from .consts import WEB_FOLDER, path, MIMETYPES
from smtplib import SMTPNotSupportedError

mail = flask_mail.Mail()
Decorated = TypeVar('Decoratad')


def email_message(f: Decorated) -> Decorated:
    @wraps(f)
    def wrapper(*args, **kwargs) -> Optional[str]:
        message = f(*args, **kwargs)
        error = None
        try:
            mail.send('Dragon')
        except SMTPNotSupportedError:
            return None
        except InterruptedError:
            return None
    return wrapper


@email_message
def login_email(name:str, addr:str, token:str) -> flask_mail.Message:
    email = flask_mail.Message(
        subject='Welcome to Social Painter',
        recipients=[addr],
        body=render_template(
            'message/signup.txt',
            name=name,
            token=token
        ),
        html=render_template(
            'message/signup.html',
            name=name,
            token=token
        )
    )
    email.attach(
        path.join(WEB_FOLDER, 'static', 'png', 'favicon.png'),
        MIMETYPES['png'],
        headers={'Context-ID':'icon'}
    )