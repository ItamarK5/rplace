
from flask import current_app
import inspect
import re
from flask_security.forms import (
    email_required, email_validator, unique_user_email,
    BaseForm, password_required, EqualTo,
    password_length, password_required, request, config_value,
    get_message
)
from wtforms import (
    PasswordField, StringField, Field
)
from copy import deepcopy
from typing import Dict, Tuple
from .security import datastore


# override
password_length.max = 128

# constants
PASSWORD_TITLE = 'One password to control your account so keep it safe, It must only contain 6-15 abc chars or digits'
RETYPE_PASSWORD_TITLE ='You must re-enter your password, so we be really sure that know your password'
USERNAME_TITLE = 'Your name, it must contain 5-15 characters and contains only abc chars\\digits'
EMAIL_TITLE = 'Your email address, so we can send it weekly adds'
reUSER = ''


def _unique_username(form, field):
    if datastore.find_user(field.data) is not None:
        raise f'Username {field.data} already exists'


class SecurityFieldMixin(object):
    placement: Dict[str, Tuple[str, str]]

    @classmethod
    def _add_tooltip(cls, field:Field, title: str, placement: str) -> None:
        field.render_kw.update({
            'data-toggle': 'tooltip',
            'title': title,
            'data-placement':placement
        })


class UniqueEmailFormMixin(SecurityFieldMixin):
    user = None
    email = StringField(
        'Email',
        validators=[email_required, email_validator, unique_user_email]
    )

    def __init_subclass__(cls, **kwargs):
        if 'email' in cls.placement:
            cls._add_tooltip(cls.email, *cls.placement['email'])


class PasswordFormMixin(SecurityFieldMixin):
    password = PasswordField(
        'Password',
        validators=[password_required]
    )

    def __init_subclass__(cls, **kwargs):
        if 'password' in cls.placement:
            cls._add_tooltip(cls.password, *cls.placement['password'])


class PasswordConfirmFormMixin(SecurityFieldMixin):
    password_confirm = PasswordField(
        'confirm password',
        validators=[EqualTo('password', message='RETYPE_PASSWORD_MISMATCH')]
    )

    def __init_subclass__(cls, **kwargs):
        if 'repassword' in cls.placement:
            cls._add_tooltip(cls.password_confirm, *cls.placement['repassword'])


class UsernameFormMixin(SecurityFieldMixin):
    username = StringField(
        'Username',
        validators=[]
    )


class RegisterFormMixin(object):
    def to_dict(form):
        def is_field_and_user_attr(member):
            return isinstance(member, Field) and \
                hasattr(datastore.user_model, member.name)
        fields = inspect.getmembers(form, is_field_and_user_attr)
        return dict((key, value.data) for key, value in fields)



class AbstractForm(BaseForm):
    def __init_subclass__(cls, **kwargs):
        # wtforms/form.py -> FormMeta.__call__
        for name in dir(cls):
            if not name.startswith('_'):
                unbound_field = getattr(cls, name)
                if hasattr(unbound_field, '_formfield'):
                    setattr(cls, name, deepcopy(unbound_field))

    def __init__(self, *args, **kwargs):
            if current_app.testing:
                self.TIME_LIMIT = None
            super(AbstractForm, self).__init__(*args, **kwargs)


class LoginForm(AbstractForm, UsernameFormMixin, PasswordFormMixin):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        if not self.next.data:
            self.next.data = request.args.get('next', '')
        self.remember.default = config_value('DEFAULT_REMEMBER_ME')

    def validate(self):
        if not super(LoginForm, self).validate():
            return False

        self.user = datastore.get_user(self.email.data)

        if self.user is None:
            self.email.errors.append(get_message('USER_DOES_NOT_EXIST')[0])
            return False
        if not self.user.password:
            self.password.errors.append(get_message('PASSWORD_NOT_SET')[0])
            return False
        if not verify_and_update_password(self.password.data, self.user):
            self.password.errors.append(get_message('INVALID_PASSWORD')[0])
            return False
        if requires_confirmation(self.user):
            self.email.errors.append(get_message('CONFIRMATION_REQUIRED')[0])
            return False
        if not self.user.is_active:
            self.email.errors.append(get_message('DISABLED_ACCOUNT')[0])
            return False
        return True
