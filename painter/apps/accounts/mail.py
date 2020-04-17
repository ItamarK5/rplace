from os import path

from flask import render_template

from painter.others.constants import MIME_TYPES
from painter.tasks.mail_tasks import send_mail


def send_signing_up_message(name: str, address: str, token: str) -> None:
    """
    :param name: name of user
    :param address: address to send the email
    :param token: registration token in itsdangerous format
    :return: nothing
    uses celery task to send a mail asynchronously to the running app
    """
    send_mail.apply_async(
        kwargs={
            'subject': 'Welcome to Social Painter',
            'recipients': [address],
            # 2 bodys, one for mail servers that show html messages and the other the text messages
            'body': render_template('message/signup.jinja', username=name, token=token),
            'html': render_template('message/signup.html', username=name, token=token),
            # reads the
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


def send_revoke_password_message(name: str, address: str, token: str) -> None:
    """
    :param name: name of user
    :param address: address to send the email
    :param token: revoke token in itsdangerous format
    :return: nothing
    uses celery task to send a mail asynchronously to the running app
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
