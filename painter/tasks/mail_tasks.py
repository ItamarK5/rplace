"""
    containig celery tasks related to sending mails
"""

from __future__ import absolute_import

from os import path
from typing import Dict, Any, List

from flask_mail import Message

from painter.app import celery
from painter.backends.extensions import mailbox


@celery.task(name='send-mail')
def send_mail(subject: str,
              recipients: List[str],
              body: str,
              html: str,
              attachments: List[Dict[str, Any]]) -> None:
    # import app of mail
    from .mail_worker import app
    with app.app_context():
        message = Message(
            subject,
            recipients=recipients,
            body=body,
            html=html
        )
        for attach in attachments:
            with app.open_resource(path.join('web', attach['path']), attach['read_mode']) as resource:
                message.attach(
                    content_type=attach['content_type'],
                    data=resource.read(),
                    disposition=attach['disposition'],
                    headers=attach['headers']
                )
        mailbox.send(message)

