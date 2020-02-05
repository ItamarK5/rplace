from flask_login import LoginManager
from sqlalchemy import create_engine
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from .config import Config


mailbox = Mail()
db = SQLAlchemy()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
# crsf protection
crsf = CSRFProtect()
