from __future__ import absolute_import

from wtforms.validators import ValidationError
from .quick_validation import (
    UsernameFieldMixin,
    PasswordFieldMixin,
    MailAddressFieldMixin,
    IPv4AddressMixin,
    PortMixin,
    QuickForm
)
from typing import Optional
import os
from ..models.user import User
from flask_script.commands import InvalidCommand


class NewUserForm(
    QuickForm,
    UsernameFieldMixin,
    PasswordFieldMixin,
    MailAddressFieldMixin,
):

    def validate_mail_address(self, field) -> None:
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('User with the mail address already exists')

    def validate_username(self, field) -> None:
        if User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError('User with the username already exists')


class PortQuickForm(
    QuickForm,
    PortMixin
):
    pass


class IPv4QuickForm(
    QuickForm,
    IPv4AddressMixin
):
    pass


def get_absolute_if_relative(pth: str) -> str:
    return pth if os.path.isabs(pth) else os.path.abspath(pth)


def handle_get_file(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return 'Path {0} don\'t exists'.format(path)
    elif os.path.isdir(path):
        raise 'Path {0} points to a directory'.format(path)
    return None


def load_configuretion(config_path: str) -> None:
    error_text = handle_get_file(config_path)
    if error_text is not None:
        raise InvalidCommand(error_text)
