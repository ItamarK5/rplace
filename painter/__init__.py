from flask import Flask
from os import path
from .apps.accounts.helpers import TokenSerializer
from .security import login_manager
from .skio import start_save_board, sio
from .apps import accounts_router, meme_router, place_router
from .constants import WEB_FOLDER
from .config import Config  # config
from .extensions import crsf, db, mailbox


app = Flask(
    __name__,
    static_folder='',
    static_url_path='',
    template_folder=path.join(WEB_FOLDER, 'templates'),
    root_path=WEB_FOLDER
)

app.config.from_object(Config)

crsf.init_app(app)
db.init_app(app)
mailbox.init_app(app)

TokenSerializer.init_app(app)
sio.init_app(app)
login_manager.init_app(app)
# insert other staff
app.register_blueprint(accounts_router)
app.register_blueprint(meme_router)
app.register_blueprint(place_router)
db.create_all(app=app)
