from celery import Celery
# celery worker to register tasks
celery = Celery(
    __name__,
    broker_url=app.config.CELERY_BROKER_URL
)
