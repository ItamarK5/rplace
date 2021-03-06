from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import EmailField
from flask import request
from painter.models import User, SignupNameRecord, SignupMailRecord, RevokePasswordMailRecord
from painter.others.wtforms_mixins import (
    ABC_OR_DIGITS_VALIDATOR,
    USERNAME_LENGTH_VALIDATOR,
    PASSWORD_LENGTH_VALIDATOR,
    MailAddressFieldMixin,
    UsernameFieldMixin,
    HashPasswordFieldMixin,
    QuickForm
)
import math


"""
FlaskForms Mixin
use mixin for making the size of the file smaller
"""


class FlaskUsernameMixin(object):
    """
    class: FlaskUsernameMixin
    contains username string field
    """
    username = StringField(
        'username',
        validators=[
            validators.data_required(),  # required
            ABC_OR_DIGITS_VALIDATOR,
            USERNAME_LENGTH_VALIDATOR
        ],
        # tooltip
        render_kw={
            'data-toggle': 'tooltip',
            'title': 'Your name, it must contain 5-15 characters and contains only abc chars\\digits',
            'data-placement': 'top'
        })


class FlaskPasswordMixin(object):
    """
    name: FlaskPasswordMixin
    mixin class for FlaskForm child
    the class member has a password field
    """
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


class FlaskConfirmPasswordMixin(FlaskPasswordMixin):
    """
    name: FlaskConfirmPasswordMixin
    mixin class for FlaskForm child to a confirm password field
    """
    confirm_password = PasswordField(
        'password confirm',
        validators=[
            validators.equal_to('password', 'Your password must match the original')
        ], render_kw={
            'data-toggle': 'tooltip',
            'title': 'You must re-enter your password, so we be really sure that know your password',
            'data-placement': 'right'
        }
    )

    def clear_data(self):
        """
        :return: none
        clears the confirm password data
        """
        self.confirm_password.data = ''


class FlaskEmailMixin(object):
    """
    name: FlaskEmailMixin
    mixin class for FlaskForm child to have a remember field,
    used for remember me option of the class
    """
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


class FlaskRememberMixin(object):
    """
    name: FlaskRememberMixin
    mixin class for FlaskForm child to have a remember field,
    used for remember me option of the class
    """
    remember = BooleanField(
        'Remember me',
        render_kw={
            'data-toggle': 'tooltip',
            'title': 'so the computer will remember your account, even if he is dating someone else',
            'data-placement': 'left'
        }
    )


class BaseForm(FlaskForm):
    """
    to shortcut staff and add staff to form
    """
    name: str  # name of the form, used in the form template, as title
    title: str  # big text in the top of the screen to show


# Real Flask Forms
class LoginForm(BaseForm,
                FlaskUsernameMixin,
                FlaskPasswordMixin,
                FlaskRememberMixin
                ):
    """
    name: LoginForm
    a login form object represent a form submitting with login information
    """
    name = 'login'
    title = 'Welcome Back to Social Painter'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.non_field_errors = []


class RefreshForm(LoginForm):
    """
    refresh user form
    its like login but without the password or email
    """
    name = 'refresh'
    title = 're-Login to your account'


class RevokePasswordForm(BaseForm,
                         FlaskEmailMixin):
    name = 'revoke'
    title = 'Change Your Password'

    # sorry pep8, but otherwise wont work
    # noinspection PyMethodMayBeStatic
    def validate_email(self, field) -> None:
        """
        :param field: the email fields
        :return: none
        extra validation for the email field, check if exists in the system
        """
        if RevokePasswordMailRecord.exists(field.data):
            interval_between_attempts_text = ''
            hours_between_each_attempt = RevokePasswordMailRecord.max_expires_seconds // 3600
            minutes_between_each_attempt = RevokePasswordMailRecord.max_expires_seconds // 60 % 60
            seconds_between_each_attempt = RevokePasswordMailRecord.max_expires_seconds % 60
            # hours
            if hours_between_each_attempt:
                interval_between_attempts_text += f'{hours_between_each_attempt} hours'
            # minutes
            if minutes_between_each_attempt:
                if interval_between_attempts_text:
                    interval_between_attempts_text += f', '
                    if not seconds_between_each_attempt:
                        interval_between_attempts_text += ', and'
                interval_between_attempts_text += f'{minutes_between_each_attempt} minutes'
            # seconds
            if seconds_between_each_attempt:
                interval_between_attempts_text += f'{seconds_between_each_attempt} seconds'
            raise ValidationError(f'You need to wait {interval_between_attempts_text} between each revoke attempt')


class ChangePasswordForm(BaseForm, FlaskConfirmPasswordMixin):
    """
    ChangePasswordForm
    a template for a form parse the second stage of changing password
    """
    name = 'Change Password'
    title = 'Set new Password'


class SignUpForm(BaseForm,
                 FlaskUsernameMixin,
                 FlaskConfirmPasswordMixin,
                 FlaskEmailMixin):
    """
    Sign up form
    a form to parse a new user information
    """
    name = 'sign-up'
    title = 'Welcome to Social Painter'

    def validate(self) -> bool:
        """
        :return: form validation
        the form adds special validation to check if a user exists with the following values
        """
        if not super().validate():
            return False
        # check if name is duplication
        is_dup_name = (
                User.query.filter_by(username=self.username.data).first() is not None
                or SignupNameRecord.exists(self.username.data)
        )
        # check if email is duplication
        is_dup_email = (
                User.query.filter_by(email=self.email.data).first() is not None
                or SignupMailRecord.exists(self.email.data)
        )
        if is_dup_name or is_dup_name:
            if is_dup_name:
                self.username.errors.append('Name already exists')
            if is_dup_email:
                self.email.errors.append('Email already exists')
            return False
        return True


# Simple Forms for validations
class SignupTokenForm(QuickForm,
                      UsernameFieldMixin,
                      MailAddressFieldMixin,
                      HashPasswordFieldMixin
                      ):
    """
    Form to parse Signup token that includes name, password and mail of the new user
    using different mixins
    """
    pass


class RevokeTokenForm(
    QuickForm,
    MailAddressFieldMixin,
    HashPasswordFieldMixin
):
    """
    Form to parse Signup token that includes name, password and mail of the new user
    using different mixin's
    """
    pass
