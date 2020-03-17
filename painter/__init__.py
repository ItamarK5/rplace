from os import path
from flask import Flask
from .constants import WEB_FOLDER
from .config import Config  # config
from celery import Celery


app = Flask(
    __name__,
    static_folder='',
    static_url_path='',
    template_folder=path.join(WEB_FOLDER, 'templates'),
    root_path=WEB_FOLDER
)

app.config.from_object(Config)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


from .skio import sio
from flask_wtf.csrf import CSRFProtect
from .apps import other_router, place_router, accounts_router, admin_router
from .extensions import datastore, mailbox, engine, login_manager, cache


sio.init_app(
    app,
    #message_queue='redis://192.168.0.214:6379/0',
)


datastore.init_app(app)
mailbox.init_app(app)
login_manager.init_app(app)
cache.init_app(app)
CSRFProtect(app)
# firebase.init_app(app)
# insert other staff
app.register_blueprint(other_router)
app.register_blueprint(place_router)
app.register_blueprint(accounts_router)
app.register_blueprint(admin_router)

import eventlet
eventlet.monkey_patch()

# include other staff
from . import filters
# backends

from .backends import extensions, board, lock
#extensions.rds_backend.init_app(app)
#board.init_app(app)
#lock.init_app(app)
datastore.create_all(app=app)
