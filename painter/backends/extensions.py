from flask_caching import Cache
from flask_login import LoginManager
from flask_mail import Mail
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from painter.config import Config

mailbox = Mail()
rds_backend = FlaskRedis()
datastore = SQLAlchemy()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
# encrypt = FlaskEncrypt()
cache = Cache(config={'CACHE_TYPE': 'simple'})
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.refresh_view = 'auth.refresh'
login_manager.needs_refresh_message = 'you need to re-login to access the information'
login_manager.needs_refresh_message_category = 'info'
