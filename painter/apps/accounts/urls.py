from __future__ import absolute_import
import time

from flask import render_template, request
from flask_login import logout_user, login_user
from werkzeug.wrappers import Response

from painter.models.storage import SignupUsernameRecord, SignupMailRecord, RevokeMailRecord
from painter.backends.extensions import datastore
from painter.models import User
from .forms import LoginForm, SignUpForm, RevokePasswordForm, ChangePasswordForm, SignUpTokenForm, RevokeTokenForm
from .mail import send_signing_up_message, send_revoke_password_message
from .utils import *


@accounts_router.route('/login', methods=('GET', 'POST'))
@anonymous_required
def login() -> Response:
    """
    :return: login page response
    """
    if current_user.is_authenticated:
        redirect('place.home')
    form = LoginForm()
    entire_form_error = []
    extra_error = None
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()  # usernames are unique
        if user is None and User.encrypt_password(form.username.data, form.password.data):
            form.password.errors.append('username and password don\'t match')
            form.username.errors.append('username and password don\'t match')
        # the only other reason it can be is that if the user is banned
        elif not login_user(user, remember=form.remember.data):
            # must be because user isnt active
            form.non_field_errors.append(user.record_message())
        else:
            return redirect(url_for('place.home'))
    # clear password
    form.password.data = ''
    return render_template('forms/index.html',
                           form=form,
                           entire_form_errors=entire_form_error,
                           extra_error=extra_error)


@accounts_router.route('/signup', methods=('GET', 'POST'))
@anonymous_required
def signup() -> Response:
    """
    :return: a response related to the registration of the user
    first requesting input
    """
    form = SignUpForm()
    if form.validate_on_submit():
        name, pswd, email = form.username.data, \
                            form.password.data, \
                            form.email.data
        # to hex to prevent any chance of decode the key and then changing it to SQL function
        pswd = User.encrypt_password(pswd, name)
        # sending the mail
        SignupUsernameRecord.force_add(name)
        SignupMailRecord.force_add(email)
        send_signing_up_message(
            name,
            email,
            TokenSerializer.signup.dumps(
                {
                    'mail_address': email,
                    'username': name,
                    'password': pswd
                }
            ))
        return render_template(
            'transport/complete-signup.html',
            username=name,
            view_ref='auth.login',
            view_name='login'
        )
    return render_template('forms/signup.html', form=form)


@accounts_router.route('/revoke', methods=['GET', 'POST'])
@anonymous_required
def revoke() -> Response:
    """
    :return: revoke password view
    """
    form = RevokePasswordForm()
    if form.validate_on_submit():
        """
        after user validation checks if the user exists
        """
        user = User.query.filter_by(email=form.email.data).first()
        RevokeMailRecord.create_new(form.email.data)
        if user is not None:
            # error handling
            send_revoke_password_message(
                user.username,
                form.email.data,
                TokenSerializer.revoke.dumps({
                    'password': user.password,
                    'mail_address': user.email
                })
            )
            render_template('transport/complete-revoke-form.html')
        else:
            """render_template('transport/revoke-unknown-user.html')"""
    return render_template('forms/revoke.html', form=form)


@accounts_router.route('/refresh', methods=['GET', 'POST'])
def refresh() -> Response:
    if current_user.is_authenticated:
        redirect('place.home')
    form = LoginForm()
    entire_form_error = []
    extra_error = None
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()  # usernames are unique
        if user is None and User.encrypt_password(form.username.data, form.password.data):
            form.password.errors.append('username and password don\'t match')
            form.username.errors.append('username and password don\'t match')
        # the only other reason it can be is that if the user is banned
        elif not login_user(user, remember=True):
            # must be because user isnt active
            form.non_field_errors.append(user.get_last_record().messsage(user.username))
        else:
            return redirect(url_for('place.home'))
    # clear password
    form.password.data = ''
    return render_template('forms/refresh.html',
                           form=form,
                           entire_form_errors=entire_form_error,
                           extra_error=extra_error)


@accounts_router.route('/change-password/<string:token>', methods=['GET', 'POST'])
@anonymous_required
def change_password(token: str) -> Response:
    """
    :param token: token url represent saving url
    :return: Response
    """
    extracted = extract_signature(
        token,
        TokenSerializer.get_max_age(),
        RevokeTokenForm,
        TokenSerializer.revoke,
    )
    # validated if any token
    if extracted is None:
        return render_template(
            'transport//revoke-error-token.html',
            view_name='Revoke Password',
            view_ref='auth.login',
        )
    # timestamp error
    if isinstance(extracted, str):
        return render_template(
            'transport//signup-token-expires.html',
            view_name='Signup',
            page_title='Over Time',
            title='Over Time',
            view_ref='auth.signup',
        )
    # else
    mail_address, pswd = extracted.pop('mail_address'), extracted.pop('password')
    # check timestamp
    user = User.query.filter_by(email=mail_address, password=pswd).first()
    if user is None or not RevokeMailRecord.exists(mail_address):
        return render_template(
            'transport//revoke-error-token.html',
            view_name='Revoke Password',
            view_ref='auth.login'
        )
    form = ChangePasswordForm()
    if not form.validate_on_submit():
        return render_template('forms/revoke-token-expires.html', form=form)
    else:
        new_password = form.password.data
        user.set_password(new_password)
    return render_template('transport/complete-signup.html')


@accounts_router.route('/logout', methods=('GET', 'POST'))
def logout() -> Response:
    if not current_user.is_anonymous:
        logout_user()
    return redirect(url_for('auth.login'))


@accounts_router.route('/confirm/<string:token>', methods=('GET',))
@anonymous_required
def confirm(token: str) -> Response:
    extracted = extract_signature(token,
                                  TokenSerializer.get_max_age(),
                                  SignUpTokenForm,
                                  TokenSerializer.signup)
    if extracted is None:
        return render_template(
            'transport//base.html',
            view_name='Sign Up',
            view_ref='auth.signup',
        )
    # else get values
    token, timestamp = extracted
    # time.timezone is the different between local time to gm-time d=(gm-local) => d+local = gm
    if (time.time() + time.timezone) >= timestamp + current_app.config['MAX_AGE_USER_SIGN_UP_TOKEN']:
        return render_template(
            'transport//base.html',
            view_name='Signup',
            title='Over Time',
            view_ref='auth.signup',
            message="you registered over time, you are late"
        )
    name, pswd, email = token.pop('username'), token.pop('password'), token.pop('email')
    # check if user exists
    # https://stackoverflow.com/a/57925308
    user = datastore.session.query(User).filter(
        User.username == name, User.password == pswd,
    ).first()
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
    user = User(
        username=name,
        password=pswd,
        email=email
    )
    datastore.session.add(user)
    datastore.session.commit()
    return render_template(
        'transport//base.html',
        title='Congrats',
        view_name='Login',
        view_ref='auth.login',
        message='Congrats, you completed registering to the social painter community,\n'
                'to continue, pless login via the login that you be redirected by pressing the button down'
    )