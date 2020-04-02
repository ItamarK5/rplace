from __future__ import absolute_import
from os import path
import eventlet
from flask import Flask
from .others.constants import WEB_FOLDER
from painter.backends.skio import sio
from painter.backends.extensions import datastore, generate_engine, mailbox, login_manager, cache, csrf
from .others import filters
# backends
from .backends import extensions, board, lock
from .apps import others, place, accounts, admin
from .others.filters import add_filters
from .worker import celery, init_celery
# monkey patch
eventlet.monkey_patch()
app = Flask(
    __name__,
    static_folder='',
    static_url_path='',
    template_folder=path.join(WEB_FOLDER, 'templates'),
)

app.config.from_pyfile('config.py')
# a must import
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
datastore.create_all(app=app)
