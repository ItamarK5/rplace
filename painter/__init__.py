from .alchemy import db, User
from .functions import *
from .settings import init_app as init_settings
from .forms import LoginForm, SignUpForm
from .consts import *
from .security import login_manager, crsf
from .views.auth_view import auth_router
from .views.meme_view import meme_router
from .skio import sio