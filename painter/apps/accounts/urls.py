"""
Accounts urls
urls of the accounts blueprint
"""
from __future__ import absolute_import

from flask import render_template
from flask_login import logout_user, login_user, login_required
from werkzeug.wrappers import Response
from typing import Type

from flask_wtf import FlaskForm
from painter.backends.extensions import storage_sql
from painter.models import SignupNameRecord, SignupMailRecord, RevokeMailAttempt, User
from painter.others.utils import redirect_next
from .router import accounts_router
from .forms import (
    LoginForm, SignUpForm, RevokePasswordForm,
    ChangePasswordForm, SignupTokenForm, RevokeTokenForm, RefreshForm
)
from .mail import send_signing_up_message, send_revoke_password_message
from .tokens import MailTokens
from .utils import *
from flask_login import login_fresh


def login_response(flask_form: Type[FlaskForm], render_html: str) -> Response:
    """
    :param flask_form: form to validate the request
    :param render_html: the page to render
    :return: login page response\refresh page
    so similar that its 1 function
    """
    # extract data
    form = flask_form()
    entire_form_error = []
    extra_error = None
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()  # usernames are unique
        # validate if user exists and if the password the form is the same as the one saved
        # the one saved is hashed
        if user is None or User.encrypt_password(form.username.data, form.password.data) != user.password:
            form.password.errors.append('username and password don\'t match')
            form.username.errors.append('username and password don\'t match')
        # the only other reason it can be is that if the user is banned
        elif not login_user(user, remember=form.remember.data):
            # must be because user isn't active
            form.non_field_errors.append(user.record_message())
        else:
            return redirect_next(url_for('place.home'))
    # clear password
    return render_template(render_html,
                           form=form,
                           entire_form_errors=entire_form_error,
                           extra_error=extra_error)


@accounts_router.route('/login', methods=('GET', 'POST'))
@anonymous_required
def login():
    """
    :return: Response login page
    just wraps the login function to make its only allowed by anonymous users
    """
    return login_response(LoginForm, 'accounts/login.html')


@accounts_router.route('/refresh', methods=('GET', 'POST'))
def refresh() -> Response:
    """
    :return: response containing the refresh message
    """
    if current_user.is_anonymous and not login_fresh():
        # redirect to home
        return redirect(url_for('paint.home'))
    # login response as fresh response
    return login_response(RefreshForm, 'accounts/refresh.html')


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
        # adding records of the name and mail addresses
        SignupNameRecord.force_add(name)
        SignupMailRecord.force_add(email)
        # sending the mail
        send_signing_up_message(
            name,
            email,
            MailTokens.signup.dumps(
                {
                    'mail_address': email,
                    'username': name,
                    'password': pswd
                }
            ))
        return render_template(
            'responses/complete-signup.html',
            username=name,
            view_ref='auth.login',
            view_name='login'
        )
    # default sign up form
    return render_template('accounts/signup.html', form=form)


@accounts_router.route('/revoke', methods=['GET', 'POST'])
@anonymous_required
def revoke() -> Response:
    """
    :return: revoke password page
    """
    form = RevokePasswordForm()
    if form.validate_on_submit():
        # after user validation checks if the user exists
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            form.email.errors.append('Unknown Mail Address')
        else:
            RevokeMailAttempt.create_new(form.email.data)
            # error handling
            send_revoke_password_message(
                user.username,
                form.email.data,
                MailTokens.revoke.dumps({
                    'password': user.password,
                    'mail_address': user.email
                })
            )
        return render_template('responses/complete-revoke.html', form=form)
    return render_template('accounts/revoke.html', form=form)


@accounts_router.route('/change-password/<string:token>', methods=['GET', 'POST'])
@anonymous_required
def change_password(token: str) -> Response:
    """
    :param token: token url represent saving url
    :return: HTML Page of the response
    """
    extracted_token = MailTokens.extract_signature(
        token,
        RevokeTokenForm,
        MailTokens.revoke,
    )
    # validated if any token
    if extracted_token is None:
        return render_template(
            'responses/token-error.html',
            view_name='Revoke Password',
            view_ref='auth.revoke',
            token_action='revoke your password'
        )
    # timestamp error
    if isinstance(extracted_token, str):
        return render_template(
            'responses/token-expires.html',
            view_name='Change Password',
            view_ref='auth.revoke',
            token_action='change your password',
        )
    # else
    mail_address, pswd = extracted_token.pop('mail_address'), extracted_token.pop('password')
    # check timestamp
    user = User.query.filter_by(email=mail_address, password=pswd).first()
    if user is None or not RevokeMailAttempt.exists(mail_address):
        return render_template(
            'responses/revoke-error-token.html',
            view_name='Revoke Password',
            view_ref='auth.revoke'
        )
    form = ChangePasswordForm()
    # if not valid new password
    if not form.validate_on_submit():
        return render_template('accounts/change-password.html', form=form)
    else:
        new_password = form.password.data
        user.set_password(new_password)
        # then forget he mail address that was passed
        RevokeMailAttempt.force_forget(mail_address)
    return render_template('responses/complete-change-password.html')


@accounts_router.route('/logout', methods=('GET',))
@login_required
def logout() -> Response:
    """
    logout response
    """
    if not current_user.is_anonymous:
        logout_user()
    return redirect(url_for('auth.login'))


@accounts_router.route('/confirm/<string:token>', methods=('GET',))
@anonymous_required
def confirm(token: str) -> Response:
    """
    :param token: a token that holds user information (username, mail and password)
    :return: response view, if use registered or not
    """
    extracted_token = MailTokens.extract_signature(token,
                                                   SignupTokenForm,
                                                   MailTokens.signup)
    if extracted_token is None:
        return render_template(
            'responses/token-error.html',
            view_name='Sign Up',
            view_ref='auth.signup',
        )
    # if got error while extracting that isn't timeout
    if extracted_token is None:
        return render_template(
            'responses/token-error.html',
            view_name='Sign Up',
            view_ref='auth.signup',
            token_action='Signing Up'
        )
    # timouet error
    if not isinstance(extracted_token, dict):
        return render_template(
            'responses/token-expires.html',
            view_name='Sign Up',
            view_ref='auth.signup',
            action_given_token='Signing Up'
        )
    # else get values
    # time.timezone is the different between local time to gm-time d=(gm-local) => d+local = gm
    name, pswd, email = extracted_token.pop('username'), extracted_token.pop('password'), extracted_token.pop('email')
    # check if user exists
    # https://stackoverflow.com/a/57925308
    user = storage_sql.session.query(User).filter(
        User.username == name, User.password == pswd,
    ).first()
    # check if user exists
    if user is not None:
        return render_template(
            'responses/reconfirm-fail.html',
            view_name='Login',
            view_ref='auth.login',
        )
    # else create user
    user = User(
        username=name,
        password=pswd,
        email=email
    )
    # save user
    storage_sql.session.add(user)
    storage_sql.session.commit()
    # return message
    return render_template(
        'responses/complete-confirm.html',
        view_name='Login',
        view_ref='auth.login',

    )
