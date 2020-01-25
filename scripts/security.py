from flask_login import LoginManager
from .alchemy import User
from flask_wtf.csrf import CSRFProtect
# crsf protection
crsf = CSRFProtect()

# login manager
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
