from flask_security import Security
from flask_login import LoginManager
from painter.constants import UserModel
from flask_security import SQLAlchemyUserDatastore
from painter.extensions import db
from painter.models.user import User, Role
from .forms import ExtendLoginForm, ExtendSignUpForm

login_manager = LoginManager()
login_manager.login_view = 'security.login'

@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))

