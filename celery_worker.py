import os
from painter.app import init_celery, celery, app

celery = init_celery(celery, app)
app.app_context().push()
