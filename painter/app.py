"""
Name: app.py
Auther Itamaer
Handles generating the app
"""
from __future__ import absolute_import
from os import path
import eventlet
from flask import Flask
from .others.constants import WEB_FOLDER
from painter.backends.skio import sio
from painter.backends.extensions import datastore, generate_engine, mailbox, login_manager, cache, csrf, redis
from .others import filters
# backends
from .backends import extensions, board, lock
from .apps import others, place, accounts, admin
from .others.filters import add_filters
from flask_socketio import SocketIO
from .worker import celery, init_celery
from typing import Union

# monkey patching
eventlet.monkey_patch()


def create_app(config_path: str = 'config.py') -> Flask:    # The Flask Application
    app = Flask(
        __name__,
        static_folder='',
        static_url_path='',
        template_folder=path.join(WEB_FOLDER, 'templates'),
    )
    # The Application Configuration, import
    app.config.from_pyfile(config_path)
    # socketio
    sio.init_app(
        app,
        # message_queue='redis://192.168.0.214:6379/0',
        # message_queue='pyamqp://guest@localhost//'  # testing
    )
    # ext
    datastore.init_app(app)
    generate_engine(app)
    mailbox.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    redis.init_app(app)
    add_filters(app)
    # insert other staff
    app.register_blueprint(place.place_router)
    app.register_blueprint(accounts.accounts_router)
    app.register_blueprint(admin.admin_router)
    app.register_blueprint(others.other_router)
    """
    extensions.rds_backend.init_app(app)
    board.init_app(app)
    lock.init_app(app)
    """
    return app
