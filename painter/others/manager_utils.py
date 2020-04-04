from __future__ import absolute_import

from wtforms.validators import ValidationError

from .user_valid import (
    UsernameFieldMixin,
    PasswordFieldMixin,
    MailAddressFieldMixin,
    QuickForm
)
from ..models.user import User


class NewUserForm(
    QuickForm,
    UsernameFieldMixin,
    PasswordFieldMixin,
    MailAddressFieldMixin,
):
    @staticmethod
    def validate_mail_address(self, field) -> None:
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('User with the mail address already exists')

    @staticmethod
    def validate_username(self, field) -> None:
        if User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError('User with the username already exists')


PAINTER_PATH = 'PAINTER-SOCIAL-CONFIG-PATHS'
