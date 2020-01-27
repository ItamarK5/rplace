from flask import Blueprint, url_for, render_template, redirect, abort
from ..alchemy import db
from ..forms import *
from ..alchemy import User
from flask_login import login_user, logout_user, current_user
from ..consts import WEB_FOLDER, path
from ..functions import encrypt_password
from http import HTTPStatus

auth_router = Blueprint('auth', 'auth', template_folder=path.join(WEB_FOLDER, 'templates'))

@auth_router.route('/', methods=('GET', ),)
def first():
    return redirect(url_for('auth.login'))


@auth_router.route('/login', methods=('GET', 'POST'),)
def login():
    """
    added in version 1.0.0
    """
    form = LoginForm()
    extra_errors = []
    if form.validate_on_submit():
        name, pswd = form.username.data, form.password.data
        pswd = encrypt_password(name, pswd)
        user = User.query.filter_by(name=name, password=pswd).first()
        if user is not None:
            print(login_user(user))
            return redirect('place')
        else:
            extra_errors.append('username or password dont match')
    form.password.data = ''
    return render_template('forms/index.html',form=form, extra_errors=extra_errors)


@auth_router.route('/signup', methods=('GET', 'POST'))
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        name, pswd, pswd2 = form.username.data, form.password.data, form.confirm_password.data
        if pswd != pswd2:
            form.confirm_password.errors.append('')
        elif User.query.filter_by(name=name).first() is not None:
            form.username.errors.append('username already exists')
        else:
           user = User(name=name, password=encrypt_password(name, pswd))
           db.session.add(user)
           db.session.commit()
           return redirect(url_for('auth.login'))
    return render_template('forms/signup.html', form=form)

@auth_router.route('/logout', methods=('GET', 'POST'))
def logout():
    if current_user.is_anonymous:
        abort(HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED)
    logout_user()
    return url_for()