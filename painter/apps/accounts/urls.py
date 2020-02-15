import time
from os import path

from flask import Blueprint, url_for, render_template, redirect, current_app, request
from flask_login import login_user, logout_user, current_user
from werkzeug.wrappers import Response

from painter.constants import WEB_FOLDER
from painter.extensions import db
from painter.models.user import User
from .forms import LoginForm, SignUpForm
from .helpers import *
from painter.models.user import Role
from .mail import send_sign_up_mail

# router blueprint -> routing all pages that relate to authorization
accounts_router = Blueprint('auth',
                            'auth',
                            template_folder=path.join(WEB_FOLDER, 'templates'))


@accounts_router.before_app_first_request
def init_tokens() -> None:
    TokenSerializer.init_serializer(current_app)


@accounts_router.route('/login', methods=('GET', 'POST'), )
def login() -> Response:
    """
    added in version 1.0.0
    :return: login page response
    """
    form = LoginForm()
    entire_form_error = []
    extra_error = None
    if form.validate_on_submit():
        name, pswd = form.username.data, User.encrypt_password(form.password.data)
        user = User.query.filter_by(username=name, password=pswd).first()
        if user is None:
            pass
        elif not login_user(user, remember=form.remember):
            extra_error = 'You cant login with non active user'
        else:
            return redirect(url_for('place.home'))
    # clear password
    form.password.data = ''
    return render_template('forms/index.html',
                           form=form,
                           entire_form_errors=entire_form_error,
                           extra_error=extra_error)


@accounts_router.route('/signup', methods=('GET', 'POST'))
def signup() -> Response:
    """
    :return: sign-up response
    """
    form = SignUpForm()
    if form.validate_on_submit():
        name, pswd, email = form.username.data, \
                            form.password.data, \
                            form.email.data
        # sending the mail
        login_error = send_sign_up_mail(name, email, TokenSerializer.signup.dumps(
            {
                'email': email,
                'username': name,
                # to hex to prevent any chance of decode the key and then changing it to SQL function
                'password': User.encrypt_password(pswd)
            }
        ))
        if login_error is not None:
            form.email.errors.append(login_error)
        else:
            return render_template('transport/complete-signup.html', username=name)
    return render_template('forms/signup.html', form=form)


@accounts_router.route('/logout', methods=('GET', 'POST'))
def logout() -> Response:
    if not current_user.is_anonymous:
        logout_user()
    return redirect(url_for('.login'))


@accounts_router.route('/confirm/<string:token>', methods=('GET',))
def confirm(token: str) -> Response:
    extracted = extract_signup_signature(token)
    if extracted is None:
        return render_template(
            'transport//base.html',
            view_name='Sign Up',
            view_ref='auth.signup',
            title='You Made a Mess',
            page_title='non valid Token',
            message='The token you entered is not valid, did you messed with him?'
                    ' if you can\'t access the original mail pless sign-up again'
        )
    # else get values
    token, timestamp = extracted
    name, pswd, email = token.pop('username'), token.pop('password'), token.pop('email')
    # check if user exists
    # https://stackoverflow.com/a/57925308
    user = db.session.query(User).filter(
        User.username == name, User.password == pswd
    ).first()
    # time.timezone is the different betwenn local time to gmtime d=(gm-local) => d+local = gm
    if (time.time() + time.timezone) - timestamp >= current_app.config['MAX_AGE_USER_SIGN_UP_TOKEN']:
        return render_template(
            'transport//base.html',
            view_name='Signup',
            title='Over Time',
            view_ref='auth.signup',
            message="you registered over time, you are late"
        )
    # check if user exists
    if user is not None:
        return render_template(
            'transport//base.html',
            view_name='Login',
            view_ref='auth.login',
            message="you already confirmed your account, if you didn\'t "
                    "maybe someone catch it before you completed, in this situation It should be recommended"
        )
    # else
    user = User(username=name, password=pswd, email=email)
    db.session.add(user)
    db.session.commit()
    return render_template(
        'transport//base.html',
        title='Congrats',
        view_name='Login',
        view_ref='auth.login',
        message='Congrats, you completed registering to the social painter community,\n'
                'to continue, pless login via the login that you be redirected by pressing the button down'
    )


@accounts_router.route('/create')
def create_user() -> Response:
    """
    :return: create user for debugging
    """
    # user = User.query.filter_by(username='socialpainter5').first()
    # if user:
    #   db.session.delete(user)
    #  db.session.commit()
    user = User(
        username=request.args['name'],
        hash_password=request.args.get('password', None) or request.args.get('pswd', None),
        email=request.args['name']+'@gmail.com'
    )
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('.login'))


@accounts_router.route('/create-admin')
def create_admin() -> Response:
    """
    :return: create user for debugging
    """
    # user = User.query.filter_by(username='socialpainter5').first()
    # if user:
    #   db.session.delete(user)
    #   db.session.commit()
    user = User(
        username='socialpainter9',
        hash_password='QWEASDZXC123',
        email='socialpainterdash@gmail.com',
        role=Role.superuser
    )
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('.login'))
