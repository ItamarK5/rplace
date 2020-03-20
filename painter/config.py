class Config:
    # ENV = 'development'
    DEBUG = True
    SEND_FILE_MAX_AGE_DEFAULT = 1
    SQLALCHEMY_DATABASE_URI = 'sqlite:///..'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = b'O\x0c\xaf\xe9\xd2\x9b#\x0f\xcaB\xa4B\xa7\xf2f:\xda5\xcf\x104\x16A\xbd'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_USERNAME = 'socialpainterdash@gmail.com'
    MAIL_PASSWORD = ',[+=dDAbg9a'
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    SESSION_PROTECTION = 'basic'
    REDIS_URL = 'redis://192.168.0.219:6379/0'
    MAIL_DEBUG = False
    MAIL_PORT = 465
    CELERY_BROKER_URL = 'pyamqp://guest@localhost//'  # 'redis://192.168.0.214:6379/0'
    MAIL_DEFAULT_SENDER = 'Social Painter Dash'
    USER_PASSWORD_SALT = b'\x20\xf8\x1a\x62\x34\x08\x48\x86\xbd\xa5\x56\x09\x34\x4a\xc5\x2c'
    USER_PASSWORD_ROUNDS = 4493  # some random 4-digit number no one would guess
    TOKEN_SIGNUP_SALT = b'MsT0FcUgSOzapJi7RAbDi5q5XWdzS3NC'
    TOKEN_REVOKE_SALT = b'2lTCKOgjMPJLCQUtpxhAv7uroIRpFwwX'
    MAX_AGE_USER_SIGN_UP_TOKEN = 3600  # 3600 seconds = 1 hour
    MAIL_MAX_EMAILS = 10
    # https://stackoverflow.com/a/54802481
    REMEMBER_COOKIE_NAME = 'SocialPainterDashCookie'
    REMEMBER_COOKIE_HTTPONLY = False
    CACHE_TYPE = 'simple'
