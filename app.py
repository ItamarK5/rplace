from painter import *
from flask import Flask
from os.path import join as path_join
from threading import Thread


def create_app():
    app = Flask(__name__,
                static_folder='',
                static_url_path='',
                template_folder=path_join(WEB_FOLDER))
    with app.app_context():
        app.config.from_object(Config)
        crsf.init_app(app)
        db.init_app(app)
        mail.init_app(app)
        login_manager.init_app(app)
        app.register_blueprint(auth_router)
        # app.register_blueprint(meme_router)
        app.register_blueprint(other_router)
        sio.init_app(app)
    return app


if __name__ == '__main__':
    Thread(target=save_board).start()
    sio.run(create_app(), host='0.0.0.0', port=8080, debug=True)
