from os import path


class Config:
    ENV = 'development'
    SEND_FILE_MAX_AGE_DEFAULT = 1
    SQLALCHEMY_DATABASE_URI = 'sqlite:///C:\\Cyber\\2020\\rplace\\database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = b'O\x0c\xaf\xe9\xd2\x9b#\x0f\xcaB\xa4B\xa7\xf2f:\xda5\xcf\x104\x16A\xbd'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_USERNAME = 'socialpainterdash@gmail.com'
    MAIL_PASSWORD = ',[+=dDAbg9a'
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_PORT = 587
    MAIL_DEFAULT_SENDER = 'Social Painter Dash'
    SECURITY_PASSWORD_SALT = b'\x20\xf8\x1a\x62\x34\x08\x48\x86\xbd\xa5\x56\x09\x34\x4a\xc5\x2c'
    SECURITY_SIGNUP_SALT = b'MsT0FcUgSOzapJi7RAbDi5q5XWdzS3NC'
    MAX_AGE_USER_SIGN_UP_TOKEN = 3600  # 3600 seconds = 1 hour
    MAIL_MAX_EMAILS = 10
    SECURITY_PASSWORD_HASH = 'sha512_crypt'
    SECURITY_REGISTERABLE = True
#    SECURITY_CONFIRMABLE = True
    SECURITY_REGISTER_URL = '/signup'
