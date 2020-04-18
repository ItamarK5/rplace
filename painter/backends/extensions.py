from flask_caching import Cache
from flask_login import LoginManager
from flask_mail import Mail
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from sqlalchemy import create_engine


mailbox = Mail()
redis = FlaskRedis()
datastore = SQLAlchemy()
csrf = CSRFProtect()
cache = Cache()
login_manager = LoginManager()


def generate_engine(app) -> None:
    try:
        create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    except IndexError:
        print('Configuration doesnt have SQLALCHEMY_DATABASE_URI value')


"""
setting values for flask-login
"""
# redirect all non logined clients that try access only logined clients to pages
login_manager.login_view = 'auth.login'
# redirect all non fresh clients that try access only freshed clients to pages
login_manager.refresh_view = 'auth.refresh'
# message
login_manager.needs_refresh_message = 'you need to re-login to access the information'
