from .security import security, datastore
from .mixins import LoginForm, RegisterForm, ConfirmRegisterForm


def init_security(app):
    security.init_app(app, datastore,
                      login_form=LoginForm,
                      confirm_register_form=ConfirmRegisterForm,
                      register_form=RegisterForm)