from .alchemy import db
from .config import Config
from .consts import WEB_FOLDER
from .security import login_manager, crsf
from .skio import sio, save_board
from .mail import mail
from .views.auth_view import auth_router
from .views.meme_view import meme_router
from .views.other_view import other_router
