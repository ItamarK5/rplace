import re
from typing import Any, Optional, Tuple, Dict, NoReturn

from flask import Flask
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from wtforms.validators import HostnameValidation

reNAME = re.compile(r'^[A-Z0-9]{5,16}$', re.I)
rePSWD = re.compile(r'^[a-f0-9]{128}$')  # password hashed so get hash value
reEMAIL = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
    re.IGNORECASE)


class TokenSerializer:
    # https://realpython.com/handling-email-confirmation-in-flask/
    signup: URLSafeTimedSerializer

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


def validate_mail(mail_address: str) -> bool:
    """
    Using the validation
    :param mail_address: email address
    :return: if the email is valid
            value = field.data
    version of the code in wtforms.validators.Email.__call__
        ...
        message = self.message
        if message is None:
            message = field.gettext('Invalid email address.')

        if not value or '@' not in value:
            raise ValidationError(message)

        user_part, domain_part = value.rsplit('@', 1)

        if not self.user_regex.match(user_part):
            raise ValidationError(message)

        if not self.validate_hostname(domain_part):
            raise ValidationError(message)
    """
    if not mail_address or '@' not in mail_address:
        return False
    user_part, domain_part = mail_address.rsplit('@', 1)
    if not reEMAIL.match(user_part):
        return False
    return HostnameValidation(require_tld=True)(domain_part)


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
    if (not mail_address) or not validate_mail(mail_address):
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
