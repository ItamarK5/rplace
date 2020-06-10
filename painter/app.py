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
from flask_script.commands import InvalidCommand

from painter.backends.extensions import (
    storage_sql, generate_engine,
    mailbox, login_manager, cache,
    csrf, redis_store
)
from painter.backends.skio import sio
from painter.models import init_storage_models
from .others.filters import add_filters

# celery worker to register tasks
celery = Celery(
    __name__,
)


def create_app(import_class: Optional[str] = None,
               is_celery: bool = False) -> Flask:
    """
    the command to create default app, with configuration
    :param import_class: the class to import from config.py as configuration base
    :param is_celery: does the app is used for celery worker context
    :return: a Flask application
    creates the application
    """
    app = Flask(
        __name__,  # the name from where to import the application
        static_folder='',
        static_url_path='',
        template_folder=path.join('web', 'templates'),
    )
    # The Application Configuration, import default
    import_object = import_class if import_class is not None else 'FlaskApp'
    # first checks if its from directly
    ref_object = 'painter.config.' + import_object
    # try import object
    app.config.from_object(ref_object)
    # socketio, not socketio in celery
    if not is_celery:
        # init socketio with eventlet
        sio.init_app(app, async_mode='eventlet')
    # set broker url if exists in app
    # celery broker url must be set directly
    # configure is celery worker configuration value
    celery.conf.update(app.config)
    storage_sql.init_app(app)
    generate_engine(app)
    mailbox.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    redis_store.init_app(app)
    celery.conf.update(app.config)
    # add filters
    add_filters(app)
    # init storage models
    init_storage_models(app)
    # import blueprint
    from .apps import others, place, accounts, admin
    app.register_blueprint(place.place_router)
    app.register_blueprint(accounts.accounts_router)
    app.register_blueprint(admin.admin_router)
    app.register_blueprint(others.other_router)
    return app
