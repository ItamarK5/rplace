
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
    SECURITY_PASSWORD_SALT = '\x20\xf8\x1a\x62\x34\x08\x48\x86\xbd\xa5\x56\x09\x34\x4a\xc5\x2c'
    MAX_TIME_FOR_USER_TO_REGISTER = 7200  # 7200 seconds = 2 hours
    MAIL_MAX_EMAILS = 10