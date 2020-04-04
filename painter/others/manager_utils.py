from __future__ import absolute_import
from .user_valid import (
    UsernameFieldMixin,
    PasswordFieldMixin,
    MailAddressFieldMixin,
    QuickForm
)
from ..models.user import User
from ..models.role import Role
from typing import Optional
from wtforms.validators import ValidationError


class NewUserForm(
    UsernameFieldMixin,
    PasswordFieldMixin,
    MailAddressFieldMixin,
    QuickForm,
    ):

    @staticmethod
    def validate_mail_address(self, field) -> None:
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('User with the mail address already exists')

    @staticmethod
    def validate_username(self, field) -> None:
        if User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError('User with the username already exists')
