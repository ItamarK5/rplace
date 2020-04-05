from __future__ import absolute_import

from functools import wraps
from typing import Any, Optional, Tuple, Dict, Callable, Type

from flask import Flask, redirect, url_for, flash
from flask import current_app
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from ...others.quick_validation import QuickForm
from .router import accounts_router


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
        initialize the token serializer backend with the application configuration
        """
        cls.signup = URLSafeTimedSerializer(
            secret_key=app.config['SECRET_KEY'],
            salt=app.config['TOKEN_SIGNUP_SALT']
        )
        cls.revoke = URLSafeTimedSerializer(
            secret_key=app.config['SECRET_KEY'],
            salt=app.config['TOKEN_REVOKE_SALT']
        )


@accounts_router.before_app_first_request
def init_tokens() -> None:
    """
    :return: init the token generator object
    """
    TokenSerializer.init_serializer(current_app)


def extract_signature(token: str,
                      form: Type[QuickForm],
                      serializer: URLSafeTimedSerializer) -> Optional[Tuple[Any, float]]:
    """
    :param token: token, a string that was encoded by the server represent a user
    :param form:  form to validate if the token is valid
    :param serializer: URLSafeTimedSerializer object that encoded the file before
    :return: None if the token isn't valid
    else returns the timestamp of the token
    """
    try:
        token, timestamp = serializer.loads(token, return_timestamp=True)
    except SignatureExpired:
        return None
    except BadSignature as e:  # error
        print(e)
        return None
    # then
    # check type
    if not isinstance(token, dict):
        return None
    # check are valid
    if not form.are_valid(**token):
        return None
    # else
    return token, timestamp.timestamp()


def anonymous_required() -> Callable[[Callable[[Any], Any]], Any]:
    """
    :return: if the user is logined, redirects the user to another url
    decorator for a url, redirects the user if he is logined to home
    """
    def wrapped(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_anonymous:
                flash(current_app.config.get('NON_LOGIN_MESSAGE'))
                return redirect(url_for(current_app.config.get('NON_LOGIN_ROUTE')))
            # else
            return f(*args, **kwargs)
        return wrapper
    return wrapped
