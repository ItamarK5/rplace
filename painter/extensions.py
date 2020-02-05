<<<<<<< HEAD
from flask import request, session
=======
>>>>>>> parent of 9614fde... 2.4.3
from sqlalchemy import create_engine
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy, declarative_base
from flask_wtf import CSRFProtect
from .config import Config
from flask_babelex import Babel

mailbox = Mail()
db = SQLAlchemy()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
# crsf protection
crsf = CSRFProtect()
<<<<<<< HEAD

babel = Babel()


@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')
=======
>>>>>>> parent of 9614fde... 2.4.3
