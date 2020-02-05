from .security import security, datastore
from .mixins import LoginForm


def init_security(app):
    security.init_app(app, datastore)