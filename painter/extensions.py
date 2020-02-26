from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_caching import Cache
from .firebase import Firebase
from .config import Config
mailbox = Mail()
db = SQLAlchemy()
cache = Cache()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
firebase = Firebase()
# crsf protection

# only after creating the UserModel
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.refresh_view = 'auth.login'
login_manager.needs_refresh_message = 'you need to re-login to access the information'
login_manager.needs_refresh_message_category = 'info'
