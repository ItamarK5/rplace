from flask import current_app
from typing import Optional, Dict, Any, Generic, Hashable
import hashlib
from wtforms.validators import Email, ValidationError


def encrypt_password(username:str, password:str) -> str:
    return hashlib.pbkdf2_hmac('sha512',
                               current_app.config['SECURITY_PASSWORD_SALT'],
                               password.encode(),
                               10000).hex()


def get_file_type(file_path:str) -> Optional[str]:
    index_start = file_path.rfind('.', -4)   # no file extension above 4 from those I use
    if index_start == -1:
        return file_path[index_start:]
    return None


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
