from typing import Dict, List, Any, List
from painter.celery import celery
from painter.extensions import mailbox
from flask_mail import Message
from flask import current_app

@celery.task(name='send-mail')
def send_mail(subject: str,
              recipients: List[str],
              body: str,
              html: str,
              attachments: List[Dict[str, Any]]) -> None:
    # safe
    print(0)
    with current_app.app_context():
        message = Message(
            subject,
            recipients=recipients,
            body=body,
            html=html
        )
        for attach in attachments:
            with current_app.open_resource(attach['path'], attach['read_mode']) as resource:
                message.attach(
                    content_type=attach['content_type'],
                    data=resource.read(),
                    disposition=attach['disposition'],
                    headers=attach['headers']
                )
        mailbox.send(message)
    print(1)