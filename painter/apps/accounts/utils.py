from flask_login import current_user
import re
from functools import wraps
from typing import Any, Optional, Tuple, Dict, Callable, Union

from flask import Flask, flash, redirect
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from wtforms.validators import HostnameValidation

from painter.backends.extensions import cache
from painter.models.user import reNAME, rePSWD


user_regex = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
    re.IGNORECASE)


class TokenSerializer(object):
    """
    object holding itsdangerous initilizers, using the flask config
    """
    # https://realpython.com/handling-email-confirmation-in-flask/
    signup: URLSafeTimedSerializer
    revoke: URLSafeTimedSerializer

    @classmethod
    def init_serializer(cls, app: Flask) -> None:
        """
        :param app: the Application object
        :return: None
        initilize the token serializer
        """
        cls.signup = URLSafeTimedSerializer(
            secret_key=app.config['SECRET_KEY'],
            salt=app.config['TOKEN_SIGNUP_SALT']
        )
        cls.revoke = URLSafeTimedSerializer(
            secret_key=app.config['SECRET_KEY'],
            salt=app.config['TOKEN_REVOKE_SALT']
        )


def extract_signature(token: str,
                      valid_predicate: Callable[[Any], bool],
                      serializer: URLSafeTimedSerializer) -> Optional[Tuple[Any, float]]:
    try:
        token, timestamp = serializer.loads(token, return_timestamp=True)
    except SignatureExpired:
        return None
    except BadSignature as e:  # error
        print(e)
        return None
    finally:
        if not valid_predicate(token):
            return None
    return token, timestamp.timestamp()


def is_valid_address(address: str) -> bool:
    if '@' not in address:
        return False
    user_part, domain_part = address.rsplit('@', 1)
    if not user_regex.match(user_part):
        return False
    if not HostnameValidation(require_tld=False)(domain_part):
        return False
    return True


def is_valid_signup_token(token: Any) -> bool:
    """
    :param token: token passed
    :return: if the token is valid
    the token from the signup email is suppose to be a dict
    that contains 3 items ('username', 'password', 'email')
    """
    if (not isinstance(token, Dict)) or len(token) != 3:
        return False
    # name
    name = token.get('username', None)
    if (not name) or not reNAME.match(name):
        return False
    # pswd
    pswd = token.get('password', None)
    if (not pswd) or not rePSWD.match(pswd):
        return False
    # name
    mail_address = token.get('email', None)
    if (not mail_address) or not is_valid_address(mail_address):
        return False
    return True


def is_valid_change_password_token(token: Any) -> bool:
    """
    :param token: token passed
    :return: if the token is valid
    the token from the signup email is suppose to be a dict
    that contains 3 items ('username', 'password', 'email')
    """
    print(token)
    if (not isinstance(token, Dict)) or len(token) != 2:
        return False
    # name
    name = token.get('username', None)
    if (not name) or not reNAME.match(name):
        return False
    # pswd
    pswd = token.get('password', None)
    if (not pswd) or not rePSWD.match(pswd):
        return False
    # name
    return True

"""
def cache_signature_view(max_timeout: int) -> Callable:
    def decorator(f: Callable[[str], Tuple[Union[str, int], int]]) -> Callable[[str], Union[str, int]]:
        #/
        #:param f: function the gets a string (token) and returns a tuple containing user\response message
        # of the token analyzer function
        #:return: function that cached the return answer of the analyze, for speed
        #/
        @wraps(f)
        def wrapped(token: str) -> Union[str, int]:
            key = str(f) + '&' + token
            cached_value = cache.get(key)
            if cached_value is None:
                answer, timeout = f(key)
                cache.set(key, answer, timeout=min(max_timeout, timeout) if timeout is not None else max_timeout)
            return cached_value

        return wrapped
    return decorator
"""


def anonymous_required() -> Callable[[Callable[[Any], Any]], Any]:
    """
        :param message: message the user will recieve if he already logined
        :return: if the user is logined, redirects the user to another url
        decorator for a url, redirects the user if he is logined to home
    """
    def wrapped(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            if current_user.is_anonymous:
                return redirect('/home')
            # else
            return f(*args, **kwargs)
        return wrapper
    return wrapped
