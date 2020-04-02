from flask_wtf import CSRFProtect
from flask_caching import Cache
from flask_login import LoginManager
from flask_mail import Mail
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from .. import app

mailbox = Mail()
rds_backend = FlaskRedis()
datastore = SQLAlchemy()
csrf = CSRFProtect()
cache = Cache(config={'CACHE_TYPE': 'simple'})
login_manager = LoginManager()


def generate_engine(app):
    create_engine(app.config['SQLALCHEMY_DATABASE_URI'])


# setting values for flask-login
login_manager.login_view = 'auth.login'
login_manager.refresh_view = 'auth.refresh'
login_manager.needs_refresh_message = 'you need to re-login to access the information'
login_manager.needs_refresh_message_category = 'info'
