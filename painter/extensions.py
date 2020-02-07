from sqlalchemy import create_engine
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from .config import Config
from flask_login import LoginManager

mailbox = Mail()
db = SQLAlchemy()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
# crsf protection
crsf = CSRFProtect()


# only after creating the UserModel

from painter.models import user
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.refresh_view = 'auth.signup'
login_manager.needs_refresh_message = 'Someone has logined to your acccount, if you dont know who' \
                                      'pless consider changing your account'


@login_manager.user_loader
def load_user(user_id):
    return user.User.query.get(int(user_id))
