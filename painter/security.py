from flask_login import LoginManager
from .alchemy import User
from flask_wtf.csrf import CSRFProtect
from itsdangerous import URLSafeTimedSerializer


# crsf protection
crsf = CSRFProtect()

# login manager
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.login_view = 'auth.login'