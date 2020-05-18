"""
Author: Itamar Kanne
file to start the celery from, and define the application its using
the flask application celery using is for its configuration options so
it can send mails using the flask-mail extension

This is for the special celery worker that also cleans the cache
"""
from painter.app import create_app, celery
from . import tasks
from celery import Celery
from ..models import ExpireModels
app = create_app(
    import_class='CeleryApp',
    is_celery=True
)


@celery.task
def clear_cache():
    """
    :return: None
    clears sql cache
    """
    for model_class in ExpireModels:
        model_class.clear_cache(False)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs) -> None:
    """
    :param sender: the celery tasks
    :param kwargs: staff, needed
    :return: None
    """
    sender.add_periodic_task(
        sender.conf.get('PERIODIC_CLEAR_CACHE_SECONDS', 1200),
        clear_cache.s()
    )

app.app_context().push()

# preventing unused import statement
__all__ = ['app', 'celery', 'tasks']
