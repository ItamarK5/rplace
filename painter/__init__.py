from .alchemy import db
from .settings import init_app as init_settings
from .consts import WEB_FOLDER
from .security import login_manager, crsf
from .skio import sio
from .views.auth_view import auth_router
from .views.meme_view import meme_router
from .views.other_view import other_router
