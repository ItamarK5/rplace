from celery import Celery


def init_celery(celery, app) -> None:
    celery.conf.update(app.config)


celery = Celery(
    __name__,
    backend= 'pyamqp://guest@localhost//'
)


from typing import Dict, Any, List
from flask import current_app
from flask_mail import Message
from painter.backends.extensions import mailbox
from .celery_worker import celery

@celery.Task(name='send-mail')
def send_mail(subject: str,
              recipients: List[str],
              body: str,
              html: str,
              attachments: List[Dict[str, Any]]) -> None:
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

