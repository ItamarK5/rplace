from os import path

from flask import Flask

from .constants import WEB_FOLDER

app = Flask(
    __name__,
    static_folder='',
    static_url_path='',
    template_folder=path.join(WEB_FOLDER, 'templates'),
    root_path=WEB_FOLDER
)

from flask_wtf.csrf import CSRFProtect
from .apps import other_router, place_router, accounts_router, admin_router
from .config import Config  # config
from .extensions import db, mailbox, engine, login_manager, cache, firebase
from .skio import board, sio


app.config.from_object(Config)

db.init_app(app)
mailbox.init_app(app)
sio.init_app(app)
login_manager.init_app(app)
board.init_app(app)
cache.init_app(app)
CSRFProtect(app)
firebase.init_app(app)
# insert other staff
app.register_blueprint(other_router)
app.register_blueprint(place_router)
app.register_blueprint(accounts_router)
app.register_blueprint(admin_router)

db.create_all(app=app)
