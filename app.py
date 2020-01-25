from painter import *
from flask import Flask
from os.path import join as path_join


def create_app():
    app = Flask(__name__, static_folder='', static_url_path='', template_folder=path_join(WEB_FOLDER))
    app = init_settings(app)
    crsf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(auth_router)
    app.register_blueprint(meme_router)
    app.register_blueprint(other_router)
    sio.init_app(app)
    return app


if __name__ == '__main__':
    sio.run(create_app(), port=8080, debug=True)