from flask import Flask
from os import path
from .skio import start_save_board, sio
from .apps import other_router, place_router
from .apps.accounts.helpers import TokenSerializer
from .constants import WEB_FOLDER
from .config import Config  # config
from .extensions import crsf, db, mailbox, engine, babel
from .security import init_security


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
babel.init_app(app)
init_security(app)
TokenSerializer.init_serializer(app)
sio.init_app(app)
# insert other staff
app.register_blueprint(other_router)
app.register_blueprint(place_router)
app.before_first_request(start_save_board)
