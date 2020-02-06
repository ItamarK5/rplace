import time
from os import path
from flask import Blueprint, url_for, render_template, redirect, current_app, request
from .helpers import *
from painter.security.forms import LoginForm, SignUpForm
from .mail import send_sign_up_mail
from painter.extensions import db
from flask_login import login_user, logout_user, current_user, login_required
from painter.constants import WEB_FOLDER
from ...constants import UserModel
from werkzeug.wrappers import Response
# router blueprint -> routing all pages that relate to authorization
accounts_router = Blueprint('auth',
                            'auth',
                            template_folder=path.join(WEB_FOLDER, 'templates'))


@accounts_router.before_app_first_request
def init_tokens():
    TokenSerializer.init_serializer(current_app)


@accounts_router.route('/', methods=('GET',))
@login_required
def home() -> Response:
    """
    :return: return the home page
    """
    return render_template('home.html')


@accounts_router.route('/login', methods=('GET', 'POST'),)
def login() -> Response:
    """
    added in version 1.0.0
    :return: login page response
    """
    form = LoginForm()
    entire_form_error = []
    extra_error = None
    if form.validate_on_submit():
        name, pswd = form.username.data, form.password.data
        pswd = UserModel.encrypt_password(pswd)
        user = UserModel.query.filter_by(name=name, password=pswd).first()
        if user is None:
            entire_form_error.append('username or password dont match')
        elif not login_user(user):
            extra_error = 'You cant login with non active user'
        else:
            return redirect(url_for('.home'))
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
        name, pswd, pswd2, email = form.username.data,\
                                   form.password.data,\
                                   form.confirm_password.data,\
                                   form.email.data
        if pswd != pswd2:
            form.confirm_password.errors.append('You must re-enter the same password')
        else:
            # no duplication
            is_dup_name = UserModel.query.filter_by(name=name).first() is not None
            is_dup_email = UserModel.query.filter_by(email=email).first() is not None
            if is_dup_name:
                form.username.errors.append('username already exists')
            if is_dup_email:
                form.email.errors.append('email already exists')
            else:
                # sending the mail
                login_error = send_sign_up_mail(name, email, TokenSerializer.signup.dumps(
                    {
                        'email': email,
                        'name': name,
                        'password': UserModel.encrypt_password(pswd).hex()
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
            page_title='Unvalid Token',
            message='The token you entered is not valid, did you messed with him?'
                    ' if you can\'t access the original mail pless sign-up again'
        )
    # else get values
    token, timestamp = extracted
    name, pswd, mail = token.pop('name'), bytes.fromhex(token.pop('password')), token.pop('email')
    # check if user exists
    # https://stackoverflow.com/a/57925308
    user = db.session.query(UserModel).filter(
        UserModel.name == name, UserModel.password == pswd
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
    user = UserModel(name=name, password=pswd, email=mail)
    db.session.add(user)
    db.session.commit()
    return render_template(
        'transport//base.html',
        view_name='Login',
        view_ref='auth.login',
        message='Congrats, you completed registering to the social painter community,\n'
                'to continue, pless login via the login that you be redirected by pressing the button down'
    )

@accounts_router.route('/create')
def create_user() -> Response:
    user = UserModel.query.filter_by(name='socialpainter5').first()
    if user:
        db.session.delete(user)
    db.session.commit()
    user = UserModel(
        name='socialpainter5',
        password=UserModel.encrypt_password('QWEASDZXC123'),
        email='socialpainterdash@gmail.com',
        role=UserModel.Role.admin
    )
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('.login'))