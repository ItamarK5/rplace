from os import path
from flask import current_app
from flask import render_template
from flask_mail import Message
from painter.others.constants import MIME_TYPES
from .tasks import send_mail


def send_sign_up_mail(name: str, address: str, token: str) -> bool:
    """
    :param name: name of user
    :param address: address to send the email
    :param token: registration token
    :return: the email message
    by because decorator email_message returns if the email was sent successfully
    """
    with current_app.app_context():
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
        current_app.extensions['mail'].send(message)
        return True


def send_revoke_password(name: str, address: str, token: str) -> None:
    """
    :param name: name of user
    :param address: address to send the email
    :param token: registration token
    :return: nothing
    uses celery task to send a mail asynchronly to the running app
    """
    send_mail.apply_async(
        kwargs={
            'subject': 'Forgot your password?',
            'recipients': [address],
            'body': render_template('message/revoke.jinja', username=name, token=token),
            'html': render_template('message/revoke.html', username=name, token=token),
            'attachments': [
                {
                    'path': path.join('static', 'png', 'favicon.png'),
                    'read_mode': 'rb',
                    'content_type': MIME_TYPES['png'],
                    'disposition': 'inline',
                    'headers': [('Content-ID', '<favicon>')]
                }
            ]
    })