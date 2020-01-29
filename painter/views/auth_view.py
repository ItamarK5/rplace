from flask import Blueprint, url_for, render_template, redirect, abort, flash, current_app
from ..alchemy import db
from ..forms import SignUpForm, LoginForm
from ..alchemy import User
from flask_login import login_user, logout_user, current_user
from ..consts import WEB_FOLDER, path
from ..functions import encrypt_password
from ..token import generate_confirmation_token, confirm_token
from http import HTTPStatus
from ..mail import login_mail
import time

auth_router = Blueprint('auth', 'auth', template_folder=path.join(WEB_FOLDER, 'templates'))


@auth_router.route('/', methods=('GET', ),)
def first():
    """
    :return: response for user enters home page / => login page
    """
    return redirect(url_for('auth.login'))


@auth_router.route('/login', methods=('GET', 'POST'),)
def login():
    """
    added in version 1.0.0
    :return: login page response
    """
    form = LoginForm()
    entire_form_error = []
    extra_error = None
    if form.validate_on_submit():
        name, pswd = form.username.data, form.password.data
        pswd = encrypt_password(name, pswd)
        user = User.query.filter_by(name=name, password=pswd).first()
        if user is None:
            entire_form_error.append('username or password dont match')
        elif not login_user(user):
            extra_error = 'You cant login with non active user'
        else:
            flash('Logged in successfully.')
            return redirect('place')
    form.password.data = ''
    return render_template('forms/index.html',
                           form=form,
                           entire_form_errors=entire_form_error,
                           extra_error=extra_error
    )


@auth_router.route('/signup', methods=('GET', 'POST'))
def signup():
    """
    :return: sign-up response
    """
    form = SignUpForm()
    if form.validate_on_submit():
        name, pswd, pswd2, email = form.username.data,\
                                   form.password.data,\
                                   form.confirm_password.data,\
                                   form.email.data
        if pswd != pswd2:
            form.confirm_password.errors.append('You must re-enter the same password')
        else:
            # no duplication
            is_dup_name = User.query.filter_by(name=name).first() is not None
            is_dup_email = User.query.filter_by(email=email).first() is not None
            if is_dup_name:
                form.username.errors.append('username already exists')
            if is_dup_email:
                form.email.errors.append('email already exists')
            else:
                # create user
                login_error = login_mail(name, email, generate_confirmation_token(email))
                if login_error is not None:
                    form.email.errors.append(login_error)
                else:
                    user = User(
                        name=name,
                        password=encrypt_password(name, pswd),
                        email=email,
                    )
                    db.session.add(user)
                    db.session.commit()
                    return render_template('transport/complete-signup.html', username=name)
    return render_template('forms/signup.html', form=form)


@auth_router.route('/logout', methods=('GET', 'POST'))
def logout():
    if current_user.is_anonymous:
        abort(HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED)
    logout_user()
    return redirect(url_for('.login'))


@auth_router.route('/confirm/<token>', methods=('GET',))
def confirm(token):
    error_text = None
    try:
        email, timestamp = confirm_token(token)
    except Exception as e:
        print(e)
    # handle timeout or user known
    user = User.query.filter_by(email=email).first_or_404()
    if user is None:
        error_text = 'Unknown User'
    # don't allow a user that is already active
    elif user.is_active:
        error_text = 'User is active'
    elif time.time() - timestamp > current_app.config.MAX_TIME_FOR_USER_TO_REGISTER:
        error_text = 'timeout'
    else:
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('main.login'))