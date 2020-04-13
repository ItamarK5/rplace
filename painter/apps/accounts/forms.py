from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import EmailField

from painter.models.user import User
from painter.others.quick_validation import (
    ABC_OR_DIGITS_VALIDATOR,
    USERNAME_LENGTH_VALIDATOR,
    PASSWORD_LENGTH_VALIDATOR,
    MailAddressFieldMixin,
    UsernameFieldMixin,
    HashPasswordFieldMixin,
    QuickForm
)
from painter.models import SignupNameRecord, SignupMailRecord, RevokeMailAttempt

"""
FlaskForms Mixin
"""


class FlaskUsernameMixin(object):
    username = StringField(
        'username',
        validators=[
            validators.data_required(),
            ABC_OR_DIGITS_VALIDATOR,
            USERNAME_LENGTH_VALIDATOR
        ],
        render_kw={
            'data-toggle': 'tooltip',
            'title': 'Your name, it must contain 5-15 characters and contains only abc chars\\digits',
            'data-placement': 'top'
        })


class FlaskPasswordMixin(object):
    password = PasswordField(
        'password',
        validators=[
            validators.data_required('You must enter something'),
            ABC_OR_DIGITS_VALIDATOR,
            PASSWORD_LENGTH_VALIDATOR,
        ],
        render_kw={
            'data-toggle': 'tooltip',
            'title': 'One password to control your account so keep it safe, ' +
                     'It must only contain 6-15 abc chars or digits',
            'data-placement': 'bottom'
        }
    )


class FlaskConfirmPasswordMixin(object):
    confirm_password = PasswordField(
        'password confirm',
        validators=[
            validators.equal_to('password', 'Your password must match the origianl')
        ], render_kw={
            'data-toggle': 'tooltip',
            'title': 'You must re-enter your password, so we be really sure that know your password',
            'data-placement': 'right'
        }
    )


class FlaskEmailMixin(object):
    email = EmailField(
        'Email',
        validators=[
            validators.data_required('You must enter a email'),
            validators.Email(),

        ], render_kw={
            'data-toggle': 'tooltip',
            # this is a joke, not really sending adds
            'title': 'Your email address, so we can send it weekly adds',
            'data-placement': 'right'
        }
    )


# Real Flask Forms
class LoginForm(FlaskForm,
                FlaskUsernameMixin,
                FlaskPasswordMixin):
    name = 'login'
    title = 'Welcome Back to Social Painter'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.non_field_errors = []

    remember = BooleanField(
        'Remember me',
        render_kw={
            'data-toggle': 'tooltip',
            'title': 'so the computer will remember your account, even if he is dating someone else',
            'data-placement': 'left'
        }
    )


class RevokePasswordForm(FlaskForm,
                         FlaskEmailMixin):
    name = 'revoke'
    title = 'Chnage Your Password'

    def validate_email(self, field) -> None:
        if RevokeMailAttempt.exists(field.data):
            raise ValidationError('You need to wait 15 minutes before you can use revoke mail again')


class ChangePasswordForm(FlaskForm,
                         FlaskPasswordMixin,
                         FlaskConfirmPasswordMixin):
    name = 'change'
    title = 'Set new Password'


class SignUpForm(FlaskForm,
                 FlaskUsernameMixin,
                 FlaskPasswordMixin,
                 FlaskConfirmPasswordMixin,
                 FlaskEmailMixin):
    name = 'sign-up'
    title = 'Welcome to Social Painter'

    def validate(self) -> bool:
        """
        :return: form validation
        the form adds special validation to check if a user exists with the following values
        """
        if not super().validate():
            return False
        is_dup_name = (
                User.query.filter_by(username=self.username.data).first() is not None
                and
                SignupNameRecord.exists(self.username.data)
        )
        is_dup_email = (
                User.query.filter_by(email=self.email.data).first() is not None
                and
                not SignupMailRecord.exists(self.email.data)
        )
        if is_dup_name or is_dup_name:
            if is_dup_name:
                self.username.errors.append('Name already exists')
            if is_dup_email:
                self.email.errors.append('Email already exists')
            return False
        return True


# Simple Forms for validations
class SignUpTokenForm(QuickForm,
                      UsernameFieldMixin,
                      MailAddressFieldMixin,
                      HashPasswordFieldMixin
                      ):
    pass


class RevokeTokenForm(
    QuickForm,
    MailAddressFieldMixin,
    HashPasswordFieldMixin
):
    pass
