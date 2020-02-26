from __future__ import annotations

import re

from flask_login import login_user
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import EmailField
from abc import ABC
from painter.models.user import User


class LoginForm(FlaskForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.non_field_errors = []
    name = 'login'
    title = 'Welcome Back to Social Painter'
    username = StringField(
        'username',
        validators=[
            validators.data_required(message='You must enter something'),
            validators.regexp(r'^[\w\d]+$', re.I, 'Input must only contain abc characters or digits'),
            validators.length(5, 15, message='The Input length isnt valid, pass a name in length between 5 to 15', )
        ],
        render_kw={
            'data-toggle': 'tooltip',
            'title': 'Your name, it must contain 5-15 characters and contains only abc chars\\digits',
            'data-placement': 'top'
        })

    password = PasswordField(
        'password',
        validators=[
            validators.data_required('You must enter something'),
            validators.regexp(r'^[\w\d]+$', re.I, 'Input must only contain abc characters or digits'),
            validators.length(6, 15, message='you have passed the length, pass name in length between 6 to 15')
        ],
        render_kw={
            'data-toggle': 'tooltip',
            'title': 'One password to control your account so keep it safe, ' +
                     'It must only contain 6-15 abc chars or digits',
            'data-placement': 'bottom'
        }
    )

    remember = BooleanField(
        'Remember me',
        render_kw={
            'data-toggle': 'tooltip',
            'title': 'so the computer will remember your account, even if he is dating someone else',
            'data-placement': 'left'
        }
    )

    def validate(self) -> bool:
        if not super().validate():
            return False
        user = User.query.filter_by(
            username=self.username.data,
            password=User.encrypt_password(self.username.data, self.password.data)
        ).first()
        if user is None:
            self.password.errors.append('username and password don\'t match')
            self.username.errors.append('username and password don\'t match')
            return False
        elif not login_user(user, remember=self.remember.data):
            # must be because user isnt active
            self.non_field_errors.append('you are banned, so your cant enter')
            return False
        return True


class RevokeForm(FlaskForm):
    name = 'revoke'
    title = 'Chnage Your Password'
    email = EmailField(
        'Email',
        validators=[
            validators.data_required('You must enter a email'),
            validators.Email('Email not valid'),

        ], render_kw={
            'data-toggle': 'tooltip',
            'title': 'Your email address, so we can send it weekly adds',
            'data-placement': 'right'
        }
    )


class ChangePasswordForm(FlaskForm):
    title = 'Set new Password'
    password = PasswordField(
        'password',
        validators=[
            validators.data_required('You must enter something'),
            validators.regexp(r'^[\w\d]+$', re.I, 'Input must only contain abc characters or digits'),
            validators.length(6, 15, message='you have passed the length, pass name in length between 6 to 15')
        ], render_kw={
            'data-toggle': 'tooltip',
            'title': 'It must only contain 6-15 abc chars or digits',
            'data-placement': 'right'
        })

    confirm_password = PasswordField(
        'password confirm',
        validators=[
            validators.equal_to('password', 'your password must match the origianl')
        ], render_kw={
            'data-toggle': 'tooltip',
            'title': 'You must re-enter your password, so we be really sure that know your password',
            'data-placement': 'right'
        })


class SignUpForm(FlaskForm):
    name = 'sign-up'
    title = 'Welcome to Social Painter'

    username = StringField(
        'username',
        validators=[
            validators.data_required(message='You must enter something'),
            validators.regexp(r'^[\w\d]+$', re.I, 'Input must only contain abc characters or digits'),
            validators.length(5, 15, message='you have passed the length, pass name in length between 5 to 15', )
        ], render_kw={
            'data-toggle': 'tooltip',
            'title': 'Your name, it must contain 5-15 characters and contains only abc chars\\digits',
            'data-placement': 'right',
        })

    password = PasswordField(
        'password',
        validators=[
            validators.data_required('You must enter something'),
            validators.regexp(r'^[\w\d]+$', re.I, 'Input must only contain abc characters or digits'),
            validators.length(6, 15, message='you have passed the length, pass name in length between 6 to 15')
        ], render_kw={
            'data-toggle': 'tooltip',
            'title': 'It must only contain 6-15 abc chars or digits',
            'data-placement': 'right'
        })

    confirm_password = PasswordField(
        'password confirm',
        validators=[
            validators.equal_to('password', 'your password must match the origianl')
        ], render_kw={
            'data-toggle': 'tooltip',
            'title': 'You must re-enter your password, so we be really sure that know your password',
            'data-placement': 'right'
        })

    email = EmailField(
        'Email',
        validators=[
            validators.data_required('You must enter a email'),
            validators.Email('Email not valid'),

        ], render_kw={
            'data-toggle': 'tooltip',
            'title': 'Your email address, so we can send it weekly adds',
            'data-placement': 'right'
        }
    )

    def validate(self) -> bool:
        if not super().validate():
            return False
        is_dup_name = User.query.filter_by(username=self.username.data).first() is not None
        is_dup_email = User.query.filter_by(email=self.email.data) is not None
        if is_dup_name or is_dup_name:
            if is_dup_name:
                self.username.errors.append('name already exists')
            if is_dup_email:
                self.email.errors.append('email already exists')
            return False
        return True
