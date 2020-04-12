"""
Name: app.py
Author: Itamar Kanne
Handles generating the app
"""
from __future__ import absolute_import

# must monkey patch
import eventlet

eventlet.monkey_patch()


from os import path
# backends
from typing import Dict, Any, Optional

from celery import Celery
from flask import Flask
from flask_script.commands import InvalidCommand

from painter.backends.extensions import (
    datastore, generate_engine,
    mailbox, login_manager, cache,
    csrf, redis
)
from painter.backends import board, lock
from painter.backends.skio import sio
from .others.constants import CELERY_TITLE
from .others.filters import add_filters
from .others.utils import get_env_path, load_configuration, set_env_path
# monkey patching

# a must set
celery = Celery(
    __name__,
    backend='amqp://guest@localhost//',
)
# to register tasks


def create_app(config_path: Optional[str] = None,
               set_env: bool = False,
               title: Optional[str] = None,
               is_celery: bool = False) -> Flask:
    """
    the command to create default app, with configuration
    :param config_path: path to JSON configuration file, if None load from environment variable
    :param set_env: if to set default enviroment
    :param title: title of the configuration option
    :param is_celery: is celery task
    :return: application
    """
    if not config_path:
        # default configure file
        if set_env:
            raise EnvironmentError('You cannot set new configuration file path without adding conf file')
        config_path = get_env_path()
    elif set_env:
        set_env_path(config_path)
    # check celery trying
    if title == CELERY_TITLE and not is_celery:
        raise InvalidCommand('Loading Configuration Error: '
                             'Celery Configuration can only be accessed by celery worker')
    elif title != CELERY_TITLE and is_celery:
        raise InvalidCommand('On Loading Configuration: '
                             'Celery worker can only access celery configuration')
    if title is None:
        print('Running with default parameters only')
    return _create_app(
        load_configuration(
            config_path,
            title.upper() if title else None
        ),
        is_celery
    )


def _create_app(config: Dict[str, Any],
                is_celery: bool = False) -> Flask:
    # first check if calls celery from none celery run
    # The Flask Application
    app = Flask(
        __name__,
        static_folder='',
        static_url_path='',
        template_folder=path.join('web', 'templates'),
    )
    # The Application Configuration, import
    # first checks if its from directly
    app.config.from_mapping(config)
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
    # insert blueprints
    from .apps import others, place, accounts, admin
    app.register_blueprint(place.place_router)
    app.register_blueprint(accounts.accounts_router)
    app.register_blueprint(admin.admin_router)
    app.register_blueprint(others.other_router)
    return app
