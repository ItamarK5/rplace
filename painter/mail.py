from flask import render_template, current_app, config
from functools import wraps
from flask_mail import Message, Mail, BadHeaderError
from typing import Optional, TypeVar
from .consts import path, MIME_TYPES


mail = Mail()
Decorated = TypeVar('Decorated')


def email_message(f: Decorated) -> Decorated:
    @wraps(f)
    def wrapper(*args, **kwargs) -> Optional[str]:
        if not current_app.config['MAIL_SUPPRESS_SEND']:
            return None
        message = f(*args, **kwargs)
        try:
            mail.send(message)
        except BadHeaderError:
            return 'Bad Header'
        return None
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
        body=render_template('message/signup.txt', username=name, token=token),
        html=render_template('message/signup.html', username=name, token=token)
    )
    with current_app.open_resource(path.join('web', 'static', 'png', 'favicon.png'), 'rb') as fp:
        email.attach(
            content_type=MIME_TYPES['png'],
            data=fp.read(),
            disposition='inline',
            headers=[('Content-ID', '<favicon>')]
        )
    return email

