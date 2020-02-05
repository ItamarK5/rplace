from flask import Flask
from os import path
<<<<<<< HEAD
from .skio import start_save_board, sio
from .apps import other_router, place_router
from .apps.accounts.helpers import TokenSerializer
from .constants import WEB_FOLDER
from .config import Config  # config
from .extensions import crsf, db, mailbox, engine, babel
from .security import init_security

=======
from .other import login_manager, babel
from .skio import start_save_board, sio
from .apps import accounts_router, other_router, place_router
from .admin import admin
from .apps.accounts.helpers import TokenSerializer
from .constants import WEB_FOLDER
from .config import Config  # config
from .extensions import crsf, db, mailbox, engine
>>>>>>> parent of 9614fde... 2.4.3

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
<<<<<<< HEAD
init_security(app)
TokenSerializer.init_serializer(app)
sio.init_app(app)
=======

TokenSerializer.init_serializer(app)
sio.init_app(app)
login_manager.init_app(app)
admin.init_app(app)
>>>>>>> parent of 9614fde... 2.4.3
# insert other staff
app.register_blueprint(accounts_router)
app.register_blueprint(other_router)
app.register_blueprint(place_router)
app.before_first_request(start_save_board)
