from werkzeug.datastructures import MultiDict
import re
from wtforms import Form, StringField,  validators

NamePattern = re.compile(r'^[A-Z0-9]{5,16}$', re.I)
HashPasswordPattern = re.compile(r'^[a-f0-9]{128}$')  # password hashed so get hash value
PasswordPattern = re.compile(r'[a-z0-9]{6,16}$')

"""
 Form Fields and messages
"""

ABC_OR_DIGITS_PATTERN = re.compile(r'^[A-Z0-9]$', re.I)
ABC_OR_DIGITS_MESSAGE = 'Field must contain only abc chars or digits'
HEX_PATTERN = re.compile(r'[a-f0-9]')
HEX_PATTERN_MESSAGE = 'Field must only contain hex values, digits or characters a to f'


USERNAME_MIN_LENGTH = 5
USERNAME_MAX_LENGTH = 16
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 16
HASH_PASSWORD_MIN_LENGTH = 64
HASH_PASSWORD_MAX_LENGTH = 64


class QuickFormMixin(Form):
    """
    Simple Form using wtforms for quick validatons
    """
    @classmethod
    def fast_validation(cls, **kwargs) -> bool:
        """
        :param kwargs: arguments to pass for the validation form
        :return: boolean if the
        a nicely class method to quick validate forms
        """
        return cls(MultiDict(**kwargs)).validate()


class MailFieldMixin(object):
    """
    MailMixn class
    a class to inherit from to add a simple validation for mail address
    uses only for validating directly without rendering it
    """
    mail_address = StringField('mail', validators=[validators.required(), validators.Email('Not valid Email')])


class PasswordFieldMixin(object):
    """
    PasswordFieldMixin class
    a class to inherit from to add a simple validation for user password
    uses only for validating directly without rendering it
    """
    password = StringField(
        'password',
        validators=[
            validators.required(),
            validators.Regexp(
                ABC_OR_DIGITS_PATTERN,
                message=ABC_OR_DIGITS_MESSAGE
            ),
            validators.Length(
                PASSWORD_MIN_LENGTH,
                PASSWORD_MAX_LENGTH
            )
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
            validators.required(),
            # hashed values can only be in hex, and there are small
            validators.Regexp(
                HEX_PATTERN,
                message=HEX_PATTERN_MESSAGE
            ),
            validators.Length(
                HASH_PASSWORD_MIN_LENGTH,
                HASH_PASSWORD_MAX_LENGTH
            )
        ]
    )


class PasswordFieldMixin(object):
    """
    PasswordFieldMixin class
    a class to inherit from to add a simple validation for user password
    uses only for validating directly without rendering it
    """
    password = StringField(
        u'password',
        validators=[
            validators.required(),
            validators.Regexp(
                ABC_OR_DIGITS_PATTERN,
                message=ABC_OR_DIGITS_MESSAGE
            ),
            validators.Length(
                PASSWORD_MIN_LENGTH,
                PASSWORD_MAX_LENGTH
            )
        ]
    )


class UsernameFieldMixin(object):
    """
    UsernameFieldMixin class
    a class to inherit from to add a simple validation for user password
    uses only for validating directly without rendering it
    """
    username = StringField(
        u'username',
        validators=[
            validators.required(),
            validators.Regexp(
                ABC_OR_DIGITS_PATTERN,
                message=ABC_OR_DIGITS_MESSAGE
            ),
            validators.Length(
                PASSWORD_MIN_LENGTH,
                PASSWORD_MAX_LENGTH
            )
        ]
    )