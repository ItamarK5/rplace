from flask import Blueprint, url_for, render_template, redirect
from ..alchemy import db
from ..forms import *
from ..alchemy import User
from flask_login import login_user
from ..consts import WEB_FOLDER, path
from ..functions import encrypt_password

auth_router = Blueprint('auth', 'auth', template_folder=path.join(WEB_FOLDER, 'templates'))


@auth_router.route('/login', methods=('GET', 'POST'),)
def login():
    """
    added in version 1.0.0
    """
    form = LoginForm()
    error_message = None    # will be used in the future for better autherazetion and login forms
    if form.validate_on_submit():
        name, pswd = form.username.data, form.password.data
        pswd = encrypt_password(name, pswd)
        user = User.query.filter_by(name=name, password=pswd).first()
        if user is not None:
            login_user(user)
            return redirect('place')
        else:
            error_message = 'username or password dont match'
    form.password.data = ''
    return render_template('forms/index.html', form=form, message=error_message)


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