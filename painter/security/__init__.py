from .security import security, datastore
<<<<<<< HEAD
from .mixins import LoginForm, CompleteRegisterForm, RegisterForm


def init_security(app):
    security.init_app(app,
                      datastore,
                      login_form=LoginForm,
=======
from .mixins import LoginForm, RegisterForm, ConfirmRegisterForm


def init_security(app):
    security.init_app(app, datastore,
                      login_form=LoginForm,
                      confirm_register_form=ConfirmRegisterForm,
>>>>>>> parent of cc4db7e... 2.4.2
                      register_form=RegisterForm)