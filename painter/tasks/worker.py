"""
Author: Itamar Kanne
file to start the celery from, and define the application its using
the flask application celery using is for its configuration options so
it can send mails using the flask-mail extension
"""
from __future__ import absolute_import
from painter.app import create_app, celery
from . import tasks

# create app context
app = create_app(is_celery=True)

app.app_context().push()
print(celery.conf.broker_url)
# preventing unused import statement
__all__ = ['app', 'celery', 'tasks']
