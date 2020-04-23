import re
from typing import Tuple

from werkzeug.datastructures import MultiDict
from wtforms import Form, StringField, validators, IntegerField, ValidationError
from painter.models import User, SignupMailRecord, SignupNameRecord

UsernamePattern = re.compile(r'^[A-Z0-9]{5,16}$', re.I)
HashPasswordPattern = re.compile(r'^[a-f0-9]{128}$')  # password hashed so get hash value

"""
 Form Fields and messages
"""

ABC_OR_DIGITS_PATTERN = re.compile(r'^[A-Z0-9]+$', re.I)
ABC_OR_DIGITS_MESSAGE = 'Field must contain only abc chars or digits'
HEX_PATTERN = re.compile(r'[a-f0-9]')
HEX_PATTERN_MESSAGE = 'Field must only contain hex values, digits or characters a to f'

USERNAME_MIN_LENGTH = 5
USERNAME_MAX_LENGTH = 16
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 16
HASH_PASSWORD_MIN_LENGTH = 128
HASH_PASSWORD_MAX_LENGTH = 128

"""
    validators
"""

# check if all values given are abc characters or numbers using regex
ABC_OR_DIGITS_VALIDATOR = validators.Regexp(
    ABC_OR_DIGITS_PATTERN,
    message=ABC_OR_DIGITS_MESSAGE
)

"""
    check if all characters are valid character in string that each char represent a byte using rgex
    used to check hashes
"""
HEX_STRING_VALIDATOR = validators.Regexp(
    HEX_PATTERN,
    message=HEX_PATTERN_MESSAGE
)

"""
    for the length validators I prefer the default validator message
"""

# wtforms validator of length of username validator field, between 5 to 15
USERNAME_LENGTH_VALIDATOR = validators.Length(
    USERNAME_MIN_LENGTH,
    USERNAME_MAX_LENGTH
)

# wtforms validator of length of password validator field, between 6 to 15
PASSWORD_LENGTH_VALIDATOR = validators.Length(
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH
)

# wtforms for hashed password
HASHED_PASSWORD_LENGTH_VALIDATOR = validators.Length(
    HASH_PASSWORD_MIN_LENGTH,
    HASH_PASSWORD_MAX_LENGTH
)


class QuickForm(Form):
    """
    Simple Form using wtforms.Form for quick validations
    """

    @classmethod
    def fast_validation(cls, **kwargs) -> Tuple['QuickForm', bool]:
        form = cls(formdata=MultiDict(dict(kwargs)))
        return form, form.validate()

    @classmethod
    def are_valid(cls, **kwargs) -> bool:
        """
        :param kwargs: arguments to pass for the validation form
        :return: boolean if the
        a nicely class method to quick validate forms
        """
        return cls.fast_validation(**kwargs)[1]


class UsernameFieldMixin(object):
    """
    UsernameFieldMixin class
    a class to inherit from to add a simple validation for user password
    uses only for validating directly without rendering it
    """
    username = StringField(
        'username',
        validators=[
            validators.data_required(),
            ABC_OR_DIGITS_VALIDATOR,
            USERNAME_LENGTH_VALIDATOR
        ]
    )


class PasswordFieldMixin(object):
    """
    PasswordFieldMixin class
    a class to inherit from to add a simple validation for user password
    uses only for validating directly without rendering it
    """
    password = StringField(
        'password',
        validators=[
            validators.data_required(),
            ABC_OR_DIGITS_VALIDATOR,
            PASSWORD_LENGTH_VALIDATOR
        ]
    )


class HashPasswordFieldMixin(object):
    """
    HashPasswordFieldMixin class
    a class to inherit from to add a simple validation for hashed password
    uses only for validating directly without rendering it
    """
    password = StringField(
        'password hashed',
        validators=[
            validators.data_required(),
            # hashed values can only be in hex, and there are small
            HEX_STRING_VALIDATOR,
            HASHED_PASSWORD_LENGTH_VALIDATOR
        ]
    )


class MailAddressFieldMixin(object):
    """
    MailAddressFieldMixin class
    a class to inherit from to add a simple validation for hashed password
    uses only for validating directly without rendering it
    """
    mail_address = StringField(
        'mail',
        validators=[
            validators.data_required(),
            validators.Email()
        ]
    )


class NewUsernameFieldMixin(UsernameFieldMixin):
    """
      same as mail field mixin
      but also validates if the email is new one
    """

    def validate_username(self, field: StringField) -> None:
        """
        :param field: username field
        :return: validates if the username isn't already existing with the name
        """
        if User.query.filter_by(username=field.data).first() is not None or\
                SignupNameRecord.exists(field.data) is not None:
            raise ValidationError('User with the mail address already exists')


class NewEmailFieldMixin(MailAddressFieldMixin):
    """
      same as mail field mixin
      but also validates if the email is new one
    """

    def validate_mail_address(self, field: StringField) -> None:
        """
        :param field:  email field
        :return: validates if the mail address isn't already existing with the name
        """
        if User.query.filter_by(email=field.data).first() is not None or\
                SignupMailRecord.exists(field.data) is not None:
            raise ValidationError('User with the mail address already exists')

