"""
Auther: Itamar Kanne
file to start the celery from, and define the application its using
the flask application celery using is for its configuration options so
it can send mails using the flask-mail extension
"""
from .app import create_app, celery
from .others.constants import CELERY_TITLE

app = create_app(title=CELERY_TITLE, is_celery=True)
app.app_context().push()

# preventing unused import statement
__all__ = ['app', 'celery']
