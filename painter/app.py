"""
Name: app.py
Author: Itamar Kanne
Handles generating the app
"""
from __future__ import absolute_import
from os import path
from typing import Optional
from celery import Celery
from flask import Flask
from painter.backends.extensions import (
    storage_sql, generate_engine,
    mailbox, login_manager, cache,
    csrf, redis
)
from painter.models import init_storage_models
from painter.backends.skio import sio
from .others.filters import add_filters
from .config import CelerySettings
import click

# celery worker to register tasks
celery = Celery(
    __name__,
)


def create_app(debug: bool = False,
               import_class: Optional[str] = None,
               is_celery: bool = False) -> Flask:
    """
    the command to create default app, with configuration
    :param import_class: the class to import from config.py as configuration base
    :param is_celery: does the app is used for celery worker context
    :param debug: if to debug app
    :return: a Flask application
    creates the application
    """
    app = Flask(
        __name__,   # the name from where to import the application
        static_folder='',
        static_url_path='',
        template_folder=path.join('web', 'templates'),
    )
    # The Application Configuration, import default
    import_object = import_class if import_class is not None else 'FlaskApp' if not is_celery else 'CeleryApp'
    # first checks if its from directly
    object_configuration = 'painter.config.' + import_object
    try:
        app.config.from_object(object_configuration)
    except ImportError:
        raise click.UsageError("Cannot import configuration {} from config.py".format(import_object))
    # socketio, not socketio in celery
    if is_celery:
        celery.conf.update({
            'result_backend': app.config['CELERY_BROKER_URL']
        })
    else:
        sio.init_app(app,
                     async_mode='eventlet')
    # set debug
    app.debug = debug
    # init Extensions
    storage_sql.init_app(app)
    generate_engine(app)
    mailbox.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    redis.init_app(app)
    celery.conf.update(app.config)
    # add filters
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
