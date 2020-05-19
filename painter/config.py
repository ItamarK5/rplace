"""
Configuration file
"""
import datetime
from abc import ABC
from typing import Optional

# region utilities
"""
Simple utility functions to simplify url building
"""


def redis_uri(
        host: str = 'localhost',
        port: int = 6379,
        database: int = 0,
        password: Optional[str] = None) -> str:
    """
    :param host: the ip of the redis server
    :param port: port to connect to redis, default 6379 the default redis port
    :param database: the number of the database in redis
    :param password: the password for the redis service, should be a big string
    (redis is so fast that one can use the authentication command
    :return: string representing a Uniform Resource Identifier (URI) to connect a redis server
    the function doesnt check if valid redis uri but created one from parameters
    """
    password = password if password else ''
    if not 0 < port < 2 ** 16:
        raise ValueError(f"Invalid port, value is {port} that isnt between 1 to 65535")
    return f'redis://:{password}@{host}:{port}/{database}'


# endregion

class FlaskDefaultSettings(ABC):
    # simple cache, because I use it in the file system
    CACHE_TYPE: str = 'simple'
    # if to send mails (True) or (Not) debug mode for mail
    MAIL_DEBUG: bool = False
    # default sender for mail
    MAIL_DEFAULT_SENDER: str = 'Social Painter Dash'
    # max number of mails to send per connection with a gmail server
    MAIL_MAX_EMAILS: datetime.timedelta = datetime.timedelta(seconds=43200)
    # password to the email account to send mails from it
    MAIL_USERNAME: str = 'socialpainterdash@gmail.com'
    MAIL_PASSWORD: str = 'EFnsDY8>.r^9n~u5FRT/%@n^'
    # port to send the mail to the mail server
    MAIL_PORT: int = 465
    # address of the mail server
    MAIL_SERVER: str = 'smtp.gmail.com'
    # if to use ssl connection for mail (as needed in gmail True)
    MAIL_USE_SSL: bool = True
    # if to use tls connection for sending the mail
    MAIL_USE_TLS: bool = False
    # max age per token creating by the TokenSerializer (Seconds
    MAX_AGE_USER_TOKEN: int = 3600
    # message sending to non logined app uses
    APP_NON_LOGIN_MESSAGE: str = 'You were redirected from pages that are for non authenticated users'
    # default route for non logined users that try access logined material
    APP_NON_LOGIN_ROUTE: str = 'place.home'
    # url for redis
    REDIS_URL: str = redis_uri(
        host='192.168.1.25',
        # default port 6379
        # default database 0
        password='UmPWoMqjGXVY7MI15rTHVKmTNRIroxcEPMVN'
    )
    #        'redis://:UmPWoMqjGXVY7MI15rTHVKmTNRIroxcEPMVN@192.168.1.25:6379/0'
    # if use remember me cookie only in http
    REMEMBER_COOKIE_HTTPONLY: bool = False
    # remember cookie name => where to save the username key for the remember me feature
    REMEMBER_COOKIE_NAME: str = 'SocialPainterDashCookie'
    # secret key for encryption
    SECRET_KEY: bytes = b'Twyv6dKbIw/KQqRCp/JmOto1zxA0FkG9'
    # number of seconds before a file
    SEND_FILE_MAX_AGE_DEFAULT: int = 4
    # session protection of the username data for flask-loginn
    SESSION_PROTECTION: str = 'basic'
    # sqlalchemy database uri
    SQLALCHEMY_DATABASE_URI: str = r'sqlite:///C:\Cyber\2020\rplace\database.db'
    # if to track modification of sqlalchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # salt for token serializer
    APP_TOKEN_REVOKE_SALT: bytes = b'MmxUQ0tPZ2pNUEpMQ1FVdHB4aEF2N3Vyb0lScEZ3d1g='
    APP_TOKEN_SIGNUP_SALT = b'TXNUMEZjVWdTT3phcEppN1JBYkRpNXE1WFdkelMzTkM='
    # number of rounds to apply hash on password
    APP_USER_PASSWORD_ROUNDS: int = 4493
    # salt for password generator
    APP_USER_PASSWORD_SALT: bytes = b'IPgaYjQISIa9pVYJNErFLA=='
    # prevent double calling of flask application on the start
    WERKZEUG_RUN_MAIN: bool = True
    # protects session from being access to external sites, Lax
    SESSION_COOKIE_SAMESITE: str = 'Lax'
    # if its a celery worker
    IS_CELERY_WORKER: bool = False
    # search host by default
    APP_HOST: str = 'search'
    # 8080 port by default
    APP_PORT: bool = 8080


class FlaskApp(FlaskDefaultSettings):
    """
    configuration for app
    """
    # app host running
    APP_HOST: str = '192.168.252.13'
    # app port running
    APP_PORT: int = 8080


class CelerySettings(ABC):
    """
    celery configuration to add options to it
    I d'idnt wanted to add any options so just pass
    """
    # a must
    IS_CELERY_WORKER: bool = True
    # broker for celery, the message queue
    CELERY_BROKER_URL: str = redis_uri(
        host='192.168.1.25',
        # default port 6379
        database=1,
        password='UmPWoMqjGXVY7MI15rTHVKmTNRIroxcEPMVN'
    )
    task_serializer = 'json',
    # content accepting serializer to allow
    accept_content = ['json'],  # Ignore other content
    # how to send back the results
    result_serializer = 'json',
    # Configure Celery to use a custom time zone.
    # The timezone value can be any time zone supported by the pytz library.
    timezone = 'UTC',
    # If enabled dates and times in messages will be converted to use the UTC timezone.
    enable_utc = True


class CeleryApp(FlaskApp, CelerySettings):
    """
    simple class for celery worker with the configuration of celery and app
    """
    pass
