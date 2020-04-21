"""
Name: app.py
Author: Itamar Kanne
Handles generating the app
"""
from __future__ import absolute_import
from os import path
# backends
from typing import Optional, Dict, Any
from celery import Celery
from flask import Flask

from painter.backends.extensions import (
    datastore, generate_engine,
    mailbox, login_manager, cache,
    csrf, redis
)
from painter.models import init_storage_models
from painter.backends.skio import sio
from .others.filters import add_filters
from .config import CelerySettings
# monkey patching

# a must set
celery = Celery(
    __name__,
    # enter the result backend
    broker=CelerySettings.CELERY_BROKER_URL
)
# to register tasks


def create_app(is_celery: bool = False, debug_mode: bool = False) -> Flask:
    """
    the command to create default app, with configuration
    :param is_celery: if the app is celery task
    :param debug_mode: if debugging app
    :return: a Flask application
    creates the application
    """
    app = Flask(
        __name__,
        static_folder='',
        static_url_path='',
        template_folder=path.join('web', 'templates'),
    )
    # The Application Configuration, import
    # first checks if its from directly
    object_configuration = 'painter.config.'
    if is_celery:
        if debug_mode:
            object_configuration += 'CeleryDebug'
        else:
            object_configuration += 'CeleryApp'
    else:
        if debug_mode:
            object_configuration += 'DebugSettings'
        else:
            object_configuration += 'AppSettings'

    app.config.from_object(object_configuration)
    # a must set
    # socketio
    sio.init_app(
        None if is_celery else app,
        message_queue='pyamqp://guest@localhost//'  # testing
    )
    # init Extensions
    datastore.init_app(app)
    generate_engine(app)
    mailbox.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    redis.init_app(app)
    celery.conf.update(app.config)
    add_filters(app)
    # init storage models
    init_storage_models(app)
    # insert blueprints
    from .apps import others, place, accounts, admin
    app.register_blueprint(place.place_router)
    app.register_blueprint(accounts.accounts_router)
    app.register_blueprint(admin.admin_router)
    app.register_blueprint(others.other_router)
    return app
