class Default:
    CACHE_TYPE = "simple"
    CELERY_BROKER_URL = "pyamqp://guest@localhost//"
    MAIL_DEBUG = "False"
    MAIL_DEFAULT_SENDER = "Social Painter Dash"
    MAIL_MAX_EMAILS = "10"
    MAIL_PASSWORD = "EFnsDY8>.r^9n~u5FRT/%@n^"
    MAIL_PORT = "465"
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_USERNAME = "socialpainterdash@gmail.com"
    MAIL_USE_SSL = "True"
    MAIL_USE_TLS = "False"
    MAX_AGE_USER_TOKEN = "3600"
    APP_NON_LOGIN_MESSAGE = "You were redirected from pages that are for non autheneticated users"
    APP_NON_LOGIN_ROUTE = "place.home"
    REDIS_URL = "redis://:UmPWoMqjGXVY7MI15rTHVKmTNRIroxcEPMVN@192.168.1.31:6379/0"
    REMEMBER_COOKIE_HTTPONLY = "False"
    REMEMBER_COOKIE_NAME = "SocialPainterDashCookie"
    SECRET_KEY = "b'Twyv6dKbIw/KQqRCp/JmOto1zxA0FkG9'"
    SEND_FILE_MAX_AGE_DEFAULT = "1"
    SESSION_PROTECTION = "basic"
    SQLALCHEMY_DATABASE_URI = "sqlite:///C:\Cyber\2020\\rplace\database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = "True"
    APP_TOKEN_REVOKE_SALT = "b'MmxUQ0tPZ2pNUEpMQ1FVdHB4aEF2N3Vyb0lScEZ3d1g='"
    APP_TOKEN_SIGNUP_SALT = "b'TXNUMEZjVWdTT3phcEppN1JBYkRpNXE1WFdkelMzTkM='"
    APP_USER_PASSWORD_ROUNDS = "4493"
    APP_USER_PASSWORD_SALT = "b'IPgaYjQISIa9pVYJNErFLA=='"
    WERKZEUG_RUN_MAIN = "True"
    SESSION_COOKIE_SAMESITE = "Lax"


class DEBUG(Default):
    """
    configuration for
    """
    APP_HOST = "127.0.0.1"
    APP_PORT = "8080"
    DEBUG = "True"


class APP(Default):
    """
    configuration for production app
    """
    APP_HOST = "192.168.1.24"
    APP_PORT = "8080"


class CELERY(Default):
    """
    configuration for celery tasks
    """
    pass
