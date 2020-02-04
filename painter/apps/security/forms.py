from __future__ import annotations
from wtforms import *
from wtforms.fields.html5 import EmailField
from flask_wtf import FlaskForm
from flask_security import RegisterForm, LoginForm
import re


class ExtendLoginForm(LoginForm):
    title = 'Welcome Back to Social Painter'
    username = StringField('username',
                           validators=[
                               validators.data_required(message='You must enter something'),
                               validators.regexp(r'^[\w\d]+$', re.I, 'Input must only contain abc characters '
                                                                     ' or digits'),
                               validators.length(5, 15, message='you have passed the length, pass name in length '
                                                                'between 5 to 15',)
                           ],
                           render_kw={
                               'data-toggle': 'tooltip',
                               'title': 'Your name, it must contain 5-15 characters and '
                                        'contains only abc chars\\digits',
                               'data-placement': 'top'
                           })

    password = PasswordField('password',
                             validators=[
                               validators.data_required('You must enter something'),
                               validators.regexp(r'^[\w\d]+$', re.I, 'Input must only contain abc characters'
                                                                     ' or digits'),
                               validators.length(6, 15, message='you have passed the length, pass name in length'
                                                                'between 6 to 15')
                            ],
                            render_kw={
                               'data-toggle': 'tooltip',
                               'title': 'One password to control your account so keep it safe, ' +
                                        'It must only contain 6-15 abc chars or digits',
                               'data-placement': 'bottom'
                            })


class ExtendSignUpForm(RegisterForm):
    title = 'Welcome to Social Painter'

    username = StringField(
        'username',
        validators=[
            validators.data_required(message='You must enter something'),
            validators.regexp(r'^[\w\d]+$', re.I, 'Input must only contain abc characters or digits'),
            validators.length(5, 15, message='you have passed the length, pass name in length between 5 to 15',)
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

    password_confirm = PasswordField(
        'password confirm',
        validators=[
            validators.data_required('You must re-enter the same password'),
            validators.regexp(r'^[\w\d]+$', re.I, 'You must re-enter the same password'),
            validators.length(6, 15, message='You must re-enter the same password')
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
