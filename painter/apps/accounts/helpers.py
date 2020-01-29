import re
from itsdangerous import URLSafeTimedSerializer, BadSignature
from flask import Flask
from typing import Any, Optional, Tuple, Dict
from wtforms.validators import Email, ValidationError


reNAME = re.compile(r'^[A-Z0-9]{5,16}$', re.I)
rePSWD = re.compile(r'^[A-F0-9]{64}$', re.I)  # password hashed so get hash value


class TokenSerializer:
    # https://realpython.com/handling-email-confirmation-in-flask/

    signup: URLSafeTimedSerializer

    @classmethod
    def init_app(cls, app: Flask) -> None:
        """
        :param app: the Application object
        :return: None
        initilize the token serializer
        """
        cls.signup = URLSafeTimedSerializer(
            secret_key=app.config['SECRET_KEY'],
            salt=app.config['SECURITY_PASSWORD_SALT']
        )


def validate_mail(mail_address: str) -> bool:
    """
    Using the validation
    :param mail_address: email address
    :return: if the email is valid (includes regex validation and domain validation)
    the Email.__call__() method
    """
    try:
        Email.__init__().__call__(None, mail_address)
    except ValidationError:
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
    name = token.get('name', None)
    if name is None or not reNAME.match(name):
        return False
    # pswd
    pswd = token.get('password', None)
    if pswd is None or not rePSWD.match(pswd):
        return False
    # name
    mail_address = token.get('email', None)
    if mail_address is None or not validate_mail(mail_address):
        return False
    return True


def extract_signup_signature(token) -> Optional[Tuple[Any, float]]:
    try:
        token, timestamp = TokenSerializer.signup.loads(token)
    except BadSignature:    # error
        return None
    finally:
        if not is_valid_signup_token(token):
            return None
    return token, timestamp
