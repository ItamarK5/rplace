from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from sqlalchemy import create_engine

from .config import Config

mailbox = Mail()
db = SQLAlchemy()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
# crsf protection
crsf = CSRFProtect()

# only after creating the UserModel
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.refresh_view = 'auth.login'
