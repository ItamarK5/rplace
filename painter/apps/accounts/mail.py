from os import path
from typing import Optional, Any, Callable, Tuple, Dict
from flask import current_app
from flask import render_template
from flask_mail import Message
from painter.constants import MIME_TYPES
from painter import celery



@celery.task
def send_message(mail_object: Message) -> None:
    current_app.extensions['mail'].send(mail_object)


def send_sign_up_mail(name: str, address: str, token: str) -> bool:
    """
    :param name: name of user
    :param address: address to send the email
    :param token: registration token
    :return: the email message
    by because decorator email_message returns if the email was sent successfully
    """
    message = Message(
        subject='Welcome to Social Painter',
        recipients=[address],
        body=render_template('message/signup.jinja', username=name, token=token),
        html=render_template('message/signup.html', username=name, token=token)
    )
    with current_app.open_resource(path.join('static', 'png', 'favicon.png'), 'rb') as fp:
        message.attach(
            content_type=MIME_TYPES['png'],
            data=fp.read(),
            disposition='inline',
            headers=[('Content-ID', '<favicon>')]
        )
    if message.has_bad_headers():
        return False
    # else
    #send_message.apply_async(args=[message])
    import time
    print(time.time())
    current_app.extensions['mail'].send(message)
    return True


def send_revoke_password(name: str, address: str, token: str) -> bool:
    """
    :param name: name of user
    :param address: address to send the email
    :param token: registration token
    :return: the email message
    by because decorator email_message returns if the email was sent successfully
    """
    message = Message(
        subject='Welcome to Social Painter',
        recipients=[address],
        body=render_template('message/revoke.jinja', username=name, token=token),
        html=render_template('message/revoke.html', username=name, token=token)
    )
    with current_app.open_resource(path.join('static', 'png', 'favicon.png'), 'rb') as fp:
        message.attach(
            content_type=MIME_TYPES['png'],
            data=fp.read(),
            disposition='inline',
            headers=[('Content-ID', '<favicon>')]
        )
    if message.has_bad_headers():
        return False
    send_message.apply_async(args=[message])
    return True
