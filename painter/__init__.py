from os import path
from flask import Flask
from .constants import WEB_FOLDER

app = Flask(
    __name__,
    static_folder='',
    static_url_path='',
    template_folder=path.join(WEB_FOLDER, 'templates'),
    root_path=WEB_FOLDER
)


from eventlet import monkey_patch
from .skio import sio
from flask_wtf.csrf import CSRFProtect
from .apps import other_router, place_router, accounts_router, admin_router
from .config import Config  # config
from .extensions import datastore, mailbox, engine, login_manager, encrypt, cache  # ,firebase


sio.init_app(
    app,
    # message_queue='redis://192.168.0.219:6379/0'
)

app.config.from_object(Config)


datastore.init_app(app)
mailbox.init_app(app)
login_manager.init_app(app)
encrypt.init_app(app)
cache.init_app(app)
CSRFProtect(app)
# firebase.init_app(app)
# insert other staff
app.register_blueprint(other_router)
app.register_blueprint(place_router)
app.register_blueprint(accounts_router)
app.register_blueprint(admin_router)

monkey_patch()
datastore.create_all(app=app)


# include other staff
from . import filters
# not backends
# from .backends import redis_backend, board, paint_lock
#redis_backend.rds_backend.init_app(app)
# board.init_app(app)
@app.before_first_request
def a():
    from .backends.accounts_cache import cache_user
    cache_user()