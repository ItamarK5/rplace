from flask import Flask
from os import path
<<<<<<< HEAD
<<<<<<< HEAD
from .skio import start_save_board, sio
from .apps import other_router, place_router
from .apps.accounts.helpers import TokenSerializer
from .constants import WEB_FOLDER
from .config import Config  # config
from .extensions import crsf, db, mailbox, engine, babel
from .security import init_security

=======
from .other import login_manager, babel
=======
from .security import login_manager
>>>>>>> parent of 300245e... 2.4.2
from .skio import start_save_board, sio
<<<<<<< HEAD
from .apps import other_router, place_router
from .security import init_security
from .constants import WEB_FOLDER
from .config import Config  # config
from .extensions import crsf, db, mailbox, engine
from .security import security
=======
from .apps import accounts_router, other_router, place_router
from .apps.accounts.helpers import TokenSerializer
from .constants import WEB_FOLDER
from .config import Config  # config
from .extensions import crsf, db, mailbox, engine
<<<<<<< HEAD
>>>>>>> parent of d54972a... 2.4.3
=======
>>>>>>> parent of 9614fde... 2.4.3

>>>>>>> parent of cc4db7e... 2.4.2

app = Flask(
    __name__,
    static_folder='',
    static_url_path='',
    template_folder=path.join(WEB_FOLDER, 'templates'),
    root_path=WEB_FOLDER
)

app.config.from_object(Config)

crsf.init_app(app)
db.init_app(app)
mailbox.init_app(app)
<<<<<<< HEAD
<<<<<<< HEAD
init_security(app)
=======

=======
babel.init_app(app)
<<<<<<< HEAD
init_security(app)
>>>>>>> parent of cc4db7e... 2.4.2
TokenSerializer.init_serializer(app)
sio.init_app(app)
=======
=======

>>>>>>> parent of 300245e... 2.4.2

TokenSerializer.init_serializer(app)
>>>>>>> parent of d54972a... 2.4.3
sio.init_app(app)
login_manager.init_app(app)
<<<<<<< HEAD
admin.init_app(app)
>>>>>>> parent of 9614fde... 2.4.3
=======
>>>>>>> parent of 300245e... 2.4.2
# insert other staff
app.register_blueprint(accounts_router)
app.register_blueprint(other_router)
app.register_blueprint(place_router)
<<<<<<< HEAD
app.before_first_request(start_save_board)
=======
db.create_all(app=app)
<<<<<<< HEAD
app.register_blueprint(place_router)
=======
>>>>>>> parent of 300245e... 2.4.2
>>>>>>> parent of cc4db7e... 2.4.2
