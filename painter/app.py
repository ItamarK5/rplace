from __future__ import absolute_import
from os import path
import eventlet
from flask import Flask
from .others.constants import WEB_FOLDER

# monkey patch
eventlet.monkey_patch()


def create_app():
    app = Flask(
        __name__,
        static_folder='',
        static_url_path='',
        template_folder=path.join(WEB_FOLDER, 'templates'),
    )

    app.config.from_pyfile('others\\config.py')
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
    # ext
    datastore.init_app(app)
    mailbox.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    CSRFProtect(app)
    # firebase.init_app(app)
    # insert other staff
    app.register_blueprint()
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
    # end creation
    return app, sio


def run_socketio(host: str = '0.0.0.0',
                 port: int = 8080, **kwargs):
    """
    :return: nothing, litterly returns nothing
    starts the app via a function
    """
    app, sio = create_app()
    sio.run(
        app,
        host,
        port,
        **kwargs
    )