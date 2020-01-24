from flask import Flask
CONFIG = {
    'ENV': 'development',
    'SEND_FILE_MAX_AGE_DEFAULT': 1,
    'SQLALCHEMY_DATABASE_URI':'sqlite:///C:\\Cyber\\2020\\rplace\\database.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': True,
    'SECRET_KEY': b'O\x0c\xaf\xe9\xd2\x9b#\x0f\xcaB\xa4B\xa7\xf2f:\xda5\xcf\x104\x16A\xbd'
}

def init_app(app:Flask):
    app.config.update(CONFIG)
    return app