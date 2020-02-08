from flask_mail import Mail, Message
from os import path
from flask import current_app, render_template
from painter.constants import MIME_TYPES
from painter.functions import send_message


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
