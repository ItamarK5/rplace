from __future__ import absolute_import

from functools import wraps
from typing import Any, Optional, Union, Dict, Callable, Type

from flask import Flask, redirect, url_for, flash, current_app
from flask_login import current_user, login_fresh
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from painter.others.constants import DEFAULT_MAX_AGE_USER_TOKEN
from painter.others.quick_validation import QuickForm
from .router import accounts_router


class TokenSerializer(object):
    """
    object holding itsdangerous initializer, using the flask config
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
            salt=app.config['APP_TOKEN_SIGNUP_SALT'],

        )
        cls.revoke = URLSafeTimedSerializer(
            secret_key=app.config['SECRET_KEY'],
            salt=app.config['APP_TOKEN_REVOKE_SALT'],
        )

    @staticmethod
    def get_max_age():
        """
        :return: the max age token
        if has max age token in configuration returns it, otherwise, returns the default one
        """
        return current_app.config.get('APP_MAX_AGE_USER_TOKEN', DEFAULT_MAX_AGE_USER_TOKEN)


@accounts_router.before_app_first_request
def init_tokens() -> None:
    """
    :return: init the token generator object
    """
    TokenSerializer.init_serializer(current_app)


def extract_signature(token: str,
                      max_age: int,
                      form: Type[QuickForm],
                      serializer: URLSafeTimedSerializer) -> Optional[Union[Dict[str, Any], str]]:
    """
    :param max_age: the maximum number of seconds that pass before the token expires
    :param token: token, a string that was encoded by the server represent a user
    :param form:  form to validate if the token is valid
    :param serializer: URLSafeTimedSerializer object that encoded the file before
    :return: None if the token isn't valid
    else returns the timestamp of the token
    """
    try:
        token = serializer.loads(
            token,
            return_timestamp=True,
            max_age=max_age
        )[0]
    except SignatureExpired:
        return 'timestamp'
    except BadSignature as e:  # error
        return None
    # then
    # check type
    if not isinstance(token, dict):
        return None
    # check are valid
    print(token)
    form.fast_validation(**token)[0].error_print()
    if not form.are_valid(**token):
        return None
    # else
    return token


def anonymous_required(f: Callable) -> Callable[[Any], Any]:
    """
    :return: if the user is logined, redirects the user to another url
    decorator for a url, redirects the user if he is logined to home
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_anonymous:
            # get from configuration
            flash(current_app.config.get('APP_NON_LOGIN_MESSAGE', 'You have to logout to access this page'))
            # redirect to home page
            return redirect(url_for(current_app.config.get('APP_NON_LOGIN_ROUTE', 'auth.home')))
        # else, run function
        return f(*args, **kwargs)
    return wrapper
