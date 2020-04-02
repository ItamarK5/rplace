from flask_mail import Message
from flask import current_app
from typing import List, Dict, Any
from celery import Celery
from .backends.extensions import mailbox

def init_celery(celery, app) -> None:
    celery.conf.update(app.config)
    return celery

celery = Celery(
    __name__,
    backend='amqp://guest@localhost//'
)


@celery.task(name='send-mail')
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

