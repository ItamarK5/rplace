from __future__ import absolute_import

from os import path

import eventlet
from flask import Flask

from .config import get_config  # config
from .others.constants import WEB_FOLDER

eventlet.monkey_patch()

app = Flask(
    __name__,
    static_folder='',
    static_url_path='',
    template_folder=path.join(WEB_FOLDER, 'templates'),
    root_path=WEB_FOLDER
)


app.config.from_object('painter.config.Config')

from painter.backends.skio import sio
from flask_wtf.csrf import CSRFProtect
from painter.backends.extensions import datastore, mailbox, engine, login_manager, cache
from . import models
# a must import


sio.init_app(
    app,
    # message_queue='redis://192.168.0.214:6379/0',
    message_queue='pyamqp://guest@localhost//'  # testing
)

datastore.init_app(app)
mailbox.init_app(app)
login_manager.init_app(app)
cache.init_app(app)
CSRFProtect(app)
# firebase.init_app(app)
# insert other staff

from .apps import place

app.register_blueprint(place.place_router)

from .apps import accounts

app.register_blueprint(accounts.accounts_router)

from .apps import admin

app.register_blueprint(admin.admin_router)

from .apps import others

app.register_blueprint(others.other_router)

# include other staff
from .others import filters

# backends
from .backends import extensions, board, lock
"""
extensions.rds_backend.init_app(app)
board.init_app(app)
lock.init_app(app)
"""
datastore.create_all(app=app)
