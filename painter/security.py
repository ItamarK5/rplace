from flask_login import LoginManager
from .constants import UserModel

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.refresh_view = 'auth.signup'
login_manager.needs_refresh_message = 'Someone has logined to your acccount, if you dont know who' \
                                      'pless consider changing your account'


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))
