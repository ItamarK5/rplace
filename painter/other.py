
from flask import request, session
from flask_login import LoginManager
from .constants import UserModel
from flask_babelex import Babel

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
babel = Babel()


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))


@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')