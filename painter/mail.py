from flask import render_template
from functools import wraps
from flask_mail import Message, Mail
from typing import Optional, TypeVar
from .consts import WEB_FOLDER, path, MIMETYPES


mail = Mail()
Decorated = TypeVar('Decoratad')


def email_message(f: Decorated) -> Decorated:
    @wraps(f)
    def wrapper(*args, **kwargs) -> Optional[str]:
        message = f(*args, **kwargs)
        with mail.connect() as conn:
            conn.send(message)
        return 'Error'
    return wrapper


@email_message
def login_mail(name: str, addr: str, token: str) -> Message:
    """
    :param name: name of user
    :param addr: address to send the email
    :param token: registrestion token
    :return: the email message
    by because decorator email_message returns if the email was sent successfully
    """
    email = Message(
        subject='Welcome to Social Painter',
        recipients=[addr],
        body=render_template(
            'message/signup.txt',
            username=name,
            token=token
        ),
        html=render_template(
            'message/signup.html',
            username=name,
            token=token
        )
    )
    email.attach(
        'favicon.png',
        content_type=MIMETYPES['png'],
        data=open(path.join(WEB_FOLDER, 'static', 'png', 'favicon.png'), 'rb').read(),
        disposition='inline',
        headers=[
            ('Content-ID', '<favicon>'),
        ]
    )
    return email
