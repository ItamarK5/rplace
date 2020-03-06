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


from eventlet import monkey_patch
from .skio import sio
from flask_wtf.csrf import CSRFProtect
from .apps import other_router, place_router, accounts_router, admin_router
from .config import Config  # config
from .extensions import db, mailbox, engine, login_manager, encrypt  # ,firebase

sio.init_app(
    app,
    # message_queue='redis://192.168.0.219:6379/0'
)

app.config.from_object(Config)


db.init_app(app)
mailbox.init_app(app)
login_manager.init_app(app)
encrypt.init_app(app)
CSRFProtect(app)
# firebase.init_app(app)
# insert other staff
app.register_blueprint(other_router)
app.register_blueprint(place_router)
app.register_blueprint(accounts_router)
app.register_blueprint(admin_router)

db.create_all(app=app)
monkey_patch()

# not backends
# from .backends import redis_backend, board, paint_lock
#redis_backend.rds_backend.init_app(app)
# board.init_app(app)