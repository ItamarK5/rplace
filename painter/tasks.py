from __future__ import absolute_import
from .others.constants import WEB_FOLDER
from typing import Dict, Any, List
from os import path
from flask_mail import Message
from painter.app import celery
from painter.backends.extensions import mailbox


@celery.task(name='send-mail')
def send_mail(subject: str,
              recipients: List[str],
              body: str,
              html: str,
              attachments: List[Dict[str, Any]]) -> None:
    from .celery_worker import app
    with app.app_context():
        message = Message(
            subject,
            recipients=recipients,
            body=body,
            html=html
        )
        for attach in attachments:
            with open(path.join(WEB_FOLDER, attach['path']), attach['read_mode']) as resource:
                message.attach(
                    content_type=attach['content_type'],
                    data=resource.read(),
                    disposition=attach['disposition'],
                    headers=attach['headers']
                )
        mailbox.send(message)

