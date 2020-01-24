from flask_login import LoginManager
from .alchemy import User

# login manager
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
