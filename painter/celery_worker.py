from .app import create_app, celery
app = create_app(main=False)
app.app_context().push()
