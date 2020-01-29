from flask import Flask
from os import path
from .extensions import crsf, db, mailbox
from .config import Config  # config
from .apps.accounts.helpers import TokenSerializer
from .security import login_manager
from .skio import save_board, sio
from .apps import accounts_router, meme_router, place_router

app = Flask(
    __name__,
    static_folder='',
    static_url_path='',
    template_folder=path.join(path.dirname(path.abspath(__file__)), 'web')
)
print(app.template_folder)

app.config.from_object(Config)
crsf.init_app(app)
db.init_app(app)
mailbox.init_app(app)
TokenSerializer.init_app(app)
sio.init_app(app)
# insert other staff
app.register_blueprint(accounts_router)
app.register_blueprint(meme_router)
app.register_blueprint(place_router)

__all__ = ['save_board', 'app', 'sio']
