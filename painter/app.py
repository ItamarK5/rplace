"""
Name: app.py
Auther Itamaer
Handles generating the app
"""
from __future__ import absolute_import

from os import path

import eventlet
from flask import Flask

from painter.backends.extensions import datastore, generate_engine, mailbox, login_manager, cache, csrf, redis
from painter.backends.skio import sio
# backends
from .others.filters import add_filters
from celery import Celery
from .others.manager_utils import get_config
# monkey patching
eventlet.monkey_patch()

# a must set
celery = Celery(
    __name__,
    backend='amqp://guest@localhost//'
)
# to register tasks


def create_app(config: str = 'config.py', main: bool = True) -> Flask:    # The Flask Application
    app = Flask(
        __name__,
        static_folder='',
        static_url_path='',
        template_folder=path.join('web', 'templates'),
    )
    # The Application Configuration, import
    # first checks if its from directly
    if config.isdigit():
        config = get_config(int(config))
    app.config.from_pyfile(config)
    # socketio
    sio.init_app(
        app if main else None,
        message_queue='pyamqp://guest@localhost//'  # testing
    )
    # ext
    datastore.init_app(app)
    generate_engine(app)
    mailbox.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    redis.init_app(app)
    celery.conf.update(app.config)
    add_filters(app)
    # insert other staff
    from .apps import others, place, accounts, admin
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
