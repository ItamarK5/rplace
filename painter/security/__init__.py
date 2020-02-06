from .security import security, datastore
from .mixins import LoginForm, CompleteRegisterForm, RegisterForm


def init_security(app):
    security.init_app(app,
                      datastore,
                      login_form=LoginForm,
                      register_form=RegisterForm)