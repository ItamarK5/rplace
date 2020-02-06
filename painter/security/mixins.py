
from flask import current_app
import inspect
import re
from flask_security.forms import (
    email_required, email_validator, unique_user_email,
<<<<<<< HEAD
    BaseForm, password_required, EqualTo,
    password_length, password_required, request, config_value,
    get_message, verify_and_update_password, NextFormMixin,
    requires_confirmation
)
from wtforms import (
    PasswordField, StringField, Field, ValidationError, BooleanField
)
from wtforms.validators import (
    Regexp, Length, Required
=======
    BaseForm, EqualTo, password_required,
    password_length, request, config_value,
    get_message, verify_and_update_password, requires_confirmation,
    NextFormMixin
)
from wtforms.validators import DataRequired, Regexp, Length
from wtforms import (
    PasswordField, StringField, Field,
    ValidationError, BooleanField
>>>>>>> parent of cc4db7e... 2.4.2
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
<<<<<<< HEAD
re_user_validator = Regexp(r'^[\w\d]+', re.I, 'username must only contain abc characters and digits')
re_password_validator = Regexp(r'^[\w\d]+', re.I, 'password must only contain abc characters and digits')
user_length_validator = Length(5, 15, 'username\'s length is between 5 to 15')
=======


username_regex = Regexp(r'^[\w\d]+', re.I, 'username must only contain ABC characters or digits')
password_regex = Regexp(r'^[\w\d]+', re.I, 'password must only contain ABC characters or digits')

username_length = Length(5, 15, 'username must be between 5 to 15 characters')
>>>>>>> parent of cc4db7e... 2.4.2


def _unique_username(form, field):
    if datastore.find_user(username=field.data) is not None:
        raise ValidationError(f'Username {field.data} already exists')


class SecurityFieldMixin(object):
    placement: Dict[str, Tuple[str, str]]

<<<<<<< HEAD
    @classmethod
    def _add_tooltip(cls, field:Field, title: str, placement: str) -> None:
        field.render_kw.update({
            'data-toggle': 'tooltip',
            'title': title,
            'data-placement': placement
        })

=======
    @staticmethod
    def _add_tooltip(field:Field, title: str, placement: str) -> None:
        field.render_kw.update({
            'data-toggle': 'tooltip',
            'title': title,
            'data-placement':placement
        })

    @staticmethod
    def can_add_tooltip(name, kwargs):
        return 'placement' in kwargs and name in kwargs['placement']

>>>>>>> parent of cc4db7e... 2.4.2

class UniqueEmailFormMixin(SecurityFieldMixin):
    user = None
    email = StringField(
        'Email',
        validators=[email_required, email_validator, unique_user_email]
    )

<<<<<<< HEAD
    def __init_subclass__(cls, **kwargs):
        if 'email' in cls.placement:
=======
    @classmethod
    def __init_subclass__(cls, **kwargs):
        cls.email = deepcopy(cls.email)
        if cls.can_add_tooltip('email', kwargs):
>>>>>>> parent of cc4db7e... 2.4.2
            cls._add_tooltip(cls.email, *cls.placement['email'])


class PasswordFormMixin(SecurityFieldMixin):
    password = PasswordField(
        'Password',
<<<<<<< HEAD
        validators=[password_required]
    )

    def __init_subclass__(cls, **kwargs):
        if 'password' in cls.placement:
=======
        validators=[
            password_required
        ]
    )

    @classmethod
    def __init_subclass__(cls, **kwargs):
        cls.password = deepcopy(cls.password)
        if cls.can_add_tooltip('password', kwargs):
>>>>>>> parent of cc4db7e... 2.4.2
            cls._add_tooltip(cls.password, *cls.placement['password'])


class PasswordConfirmFormMixin(SecurityFieldMixin):
    password_confirm = PasswordField(
<<<<<<< HEAD
        'confirm password',
        validators=[EqualTo('password', message='RETYPE_PASSWORD_MISMATCH')]
    )

    def __init_subclass__(cls, **kwargs):
        if 'repassword' in cls.placement:
=======
        'Confirm Password',
        validators=[EqualTo('password', message='RETYPE_PASSWORD_MISMATCH')]
    )

    @classmethod
    def __init_subclass__(cls, **kwargs):
        cls.password_confirm = deepcopy(cls.password_confirm)
        if cls.can_add_tooltip('repassword', kwargs):
>>>>>>> parent of cc4db7e... 2.4.2
            cls._add_tooltip(cls.password_confirm, *cls.placement['repassword'])


class UsernameFormMixin(SecurityFieldMixin):
    username = StringField(
<<<<<<< HEAD
        'Username',
        validators=[]
    )
    def __init_subclass__(cls, **kwargs):
        if 'username' in cls.placement:
            cls._add_tooltip(cls.username, *cls.placement['username'])


class UniqueUsernameFormMixin(SecurityFieldMixin):
    username = StringField(
        'Username',
        validators=[
            Required('username is required'),
            re_user_validator,
            user_length_validator,
            _unique_username
        ]
    )

    def __init_subclass__(cls, **kwargs):
        if 'username' in cls.placement:
=======
        'username',
        validators=[
            DataRequired('you must enter a username'),
            username_regex,
            username_length,
        ])

    @classmethod
    def __init_subclass__(cls, **kwargs):
        cls.username = deepcopy(cls.username)
        if cls.can_add_tooltip('username', kwargs):
            cls._add_tooltip(cls.username, *cls.placement['username'])


class NewUsernameFormMixin(UsernameFormMixin):
    username = StringField(
        'username',
        validators=[
            DataRequired('you must enter a username'),
            username_regex,
            username_length,
            _unique_username
        ])

    def __init_subclass__(cls, **kwargs):
        cls.username = deepcopy(cls.username)
        if cls.can_add_tooltip('username', kwargs):
>>>>>>> parent of cc4db7e... 2.4.2
            cls._add_tooltip(cls.username, *cls.placement['username'])


class RegisterFormMixin(object):
<<<<<<< HEAD
    def to_dict(form):
        def is_field_and_user_attr(member):
            return isinstance(member, Field) and \
                hasattr(datastore.user_model, member.name)
        fields = inspect.getmembers(form, is_field_and_user_attr)
=======
    def to_dict(self):
        def is_field_and_user_attr(member):
            return isinstance(member, Field) and \
                hasattr(datastore.user_model, member.name)
        fields = inspect.getmembers(self, is_field_and_user_attr)
>>>>>>> parent of cc4db7e... 2.4.2
        return dict((key, value.data) for key, value in fields)


class AbstractForm(BaseForm):
<<<<<<< HEAD
    def __init_subclass__(cls, **kwargs):
        # wtforms/form.py -> FormMeta.__call__
        for name in dir(cls):
            if not name.startswith('_'):
                unbound_field = getattr(cls, name)
                if hasattr(unbound_field, '_formfield'):
                    setattr(cls, name, deepcopy(unbound_field))
=======
    title: str
>>>>>>> parent of cc4db7e... 2.4.2

    def __init__(self, *args, **kwargs):
        if current_app.testing:
            self.TIME_LIMIT = None
        super(AbstractForm, self).__init__(*args, **kwargs)


class LoginForm(AbstractForm, UsernameFormMixin, PasswordFormMixin, NextFormMixin):
<<<<<<< HEAD
    remember = BooleanField('remember me')
=======
    title = 'Welcome to Social Painter'
    remember = BooleanField('Remember Me')
    placement = {
        'username': (USERNAME_TITLE, 'right'),
        'password': (PASSWORD_TITLE, 'left')
    }
>>>>>>> parent of cc4db7e... 2.4.2

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        if not self.next.data:
            self.next.data = request.args.get('next', '')
        self.remember.default = config_value('DEFAULT_REMEMBER_ME')

    def validate(self):
        if not super(LoginForm, self).validate():
            return False
<<<<<<< HEAD
        self.user = datastore.find_user(self.username.data)
        if self.user is None:
            self.password.errors.append('Invalid username or password')
            self.username.errors.append('Invalid username or password')
            return False
        if not self.user.password:
            self.password.errors.append("Password Dont Exist")
            return False
        if not verify_and_update_password(self.password.data, self.user):
            self.password.errors.append('Invalid username or password')
            self.username.errors.append('Invalid username or password')
=======
        self.user = datastore.find_user(username=self.username.data)
        if self.user is None:
            self.username.errors.append(get_message('USER_DOES_NOT_EXIST')[0])
            return False
        if not self.user.password:
            self.password.errors.append(get_message('PASSWORD_NOT_SET')[0])
            return False
        if not verify_and_update_password(self.password.data, self.user):
            self.password.errors.append(get_message('INVALID_PASSWORD')[0])
>>>>>>> parent of cc4db7e... 2.4.2
            return False
        if requires_confirmation(self.user):
            self.email.errors.append(get_message('CONFIRMATION_REQUIRED')[0])
            return False
        if not self.user.is_active:
            self.email.errors.append(get_message('DISABLED_ACCOUNT')[0])
            return False
        return True


<<<<<<< HEAD
class CompleteRegisterForm(AbstractForm, RegisterFormMixin, UniqueUsernameFormMixin,
                           PasswordFormMixin, UniqueEmailFormMixin):
    pass


class RegisterForm(CompleteRegisterForm, PasswordConfirmFormMixin):
    pass
=======
class ConfirmRegisterForm(AbstractForm, RegisterFormMixin, PasswordFormMixin,
                          UsernameFormMixin, UniqueEmailFormMixin):
    pass


class RegisterForm(ConfirmRegisterForm, PasswordConfirmFormMixin, NextFormMixin):
    title = 'Register to Social Painter'
    placement = {
        'username': (USERNAME_TITLE, 'top'),
        'password': (PASSWORD_TITLE, 'top'),
        'repassword': (EMAIL_TITLE, 'top'),
        'email': (EMAIL_TITLE, 'top')
    }

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        if not self.next.data:
            self.next.data = request.args.get('next', '')
>>>>>>> parent of cc4db7e... 2.4.2
