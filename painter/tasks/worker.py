"""
Author: Itamar Kanne
file to start the celery from, and define the application its using
the flask application celery using is for its configuration options so
it can send mails using the flask-mail extension
"""
from painter.app import create_app, celery
from . import tasks

app = create_app(
    import_class='CeleryApp',
    is_celery=True
)

app.app_context().push()

# preventing unused import statement
__all__ = ['app', 'celery', 'tasks']
