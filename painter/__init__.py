from __future__ import absolute_import
from os import path
from flask import Flask
from painter.others.constants import WEB_FOLDER
from .config import Config  # config

import eventlet
eventlet.monkey_patch()

print(path.exists(WEB_FOLDER), WEB_FOLDER)
app = Flask(
    __name__,
    static_folder='',
    static_url_path='',
    template_folder=path.join(WEB_FOLDER, 'templates'),
    root_path=WEB_FOLDER
)

app.config.from_object(Config)


from painter.backends.skio import sio
from flask_wtf.csrf import CSRFProtect
from .apps import other_router, place_router, accounts_router, admin_router
from .extensions import datastore, mailbox, engine, login_manager, cache
from .celery import celery

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


# include other staff
from .others import filters
# backends

from .backends import extensions, board, lock
# extensions.rds_backend.init_app(app)
# board.init_app(app)
# lock.init_app(app)
datastore.create_all(app=app)
