from __future__ import absolute_import

from wtforms.validators import ValidationError
from flask_script.commands import InvalidCommand
from .user_valid import (
    UsernameFieldMixin,
    PasswordFieldMixin,
    MailAddressFieldMixin,
    QuickForm
)
from ..models.user import User
from typing import Optional
import os

PAINTER_ENV_NAME = 'PAINTER-SOCIAL-CONFIG-PATHS'


class NewUserForm(
    QuickForm,
    UsernameFieldMixin,
    PasswordFieldMixin,
    MailAddressFieldMixin,
):

    def validate_mail_address(self, field) -> None:
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('User with the mail address already exists')

    @staticmethod
    def validate_username(self, field) -> None:
        if User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError('User with the username already exists')


def add_configure(config_paths: str, new_path: str, num: Optional[int]) -> Optional[str]:
    if '|' not in config_paths and num is None:
        paths = [config_paths, new_path]
    elif num is None:
        paths = config_paths.split('|')
        paths.append(new_path)
        return None
    else:
        paths = config_paths.split('|')
        paths.insert(min(num, len(config_paths)), new_path)
    return '|'.join(config_paths)


def get_config(num: int) -> str:
    # first get the
    if PAINTER_ENV_NAME not in os.environ:
        raise InvalidCommand('Cannot Access Configure')
    pths = os.environ[PAINTER_ENV_NAME]
    config_paths = [pths] if '|' not in pths else pths.split('|')
    if num >= len(config_paths):
        raise InvalidCommand("Index out of range, there are only:{0}} "
                             "options but you entered {1}".format(len(pths), num))
    # else
    return pths[num]
