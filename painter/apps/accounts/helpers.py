from typing import Any, Optional, Tuple, Dict, NoReturn

from flask import Flask
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from wtforms.validators import Email

from painter.models.user import reNAME, rePSWD


class TokenSerializer:
    # https://realpython.com/handling-email-confirmation-in-flask/
    signup: URLSafeTimedSerializer
    revoke: URLSafeTimedSerializer

    @classmethod
    def init_serializer(cls, app: Flask) -> NoReturn:
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
    if (not mail_address) or not Email()(mail_address):
        return False
    return True


def extract_signup_signature(token: str) -> Optional[Tuple[Any, float]]:
    try:
        token, timestamp = TokenSerializer.signup.loads(token, return_timestamp=True)
    except SignatureExpired:
        return None
    except BadSignature as e:  # error
        print(e)
        return None
    finally:
        if not is_valid_signup_token(token):
            return None
    return token, timestamp.timestamp()
