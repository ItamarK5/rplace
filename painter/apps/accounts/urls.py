import time
from os import path

from flask import Blueprint, url_for, render_template, redirect, current_app, request
from flask_login import logout_user, current_user, login_user
from werkzeug.wrappers import Response
from painter.constants import WEB_FOLDER
from painter.extensions import datastore
from painter.models.user import Role
from painter.models.user import User
from .forms import LoginForm, SignUpForm, RevokeForm
from .utils import *
from .mail import send_sign_up_mail, send_revoke_password

# router blueprint -> routing all pages that relate to authorization
accounts_router = Blueprint('auth',
                            'auth',
                            template_folder=path.join(WEB_FOLDER, 'templates'))


@accounts_router.before_app_first_request
def init_tokens() -> None:
    """
    :return: init the token generator
    """
    TokenSerializer.init_serializer(current_app)


@accounts_router.route('/login', methods=('GET', 'POST'), )
def login() -> Response:
    """
    added in version 1.0.0
    :return: login page response
    """
    if current_user.is_authenticated:
        redirect('place.home')
    form = LoginForm()
    entire_form_error = []
    extra_error = None
    if form.validate_on_submit():
        print(form.username.data)
        user = User.query.filter_by(username=form.username.data).first()    # usernames are unique
        if user is None and User.encrypt_password(form.username.data, form.password.data):
            form.password.errors.append('username and password don\'t match')
            form.username.errors.append('username and password don\'t match')
        # the only other reason it can be is that if the user is banned
        elif not login_user(user, remember=form.remember.data):
            # must be because user isnt active
            form.non_field_errors.append(user.get_last_record().messsage(user.username))
        else:
            return redirect(url_for('place.home'))
    """
    if request.method.lower() == 'post':
        x = time.time()
        try:
            # Verify the ID token while checking if the token is revoked by
            # passing check_revoked=True.
            decoded_token = auth.verify_id_token(request.form['token'], check_revoked=True)
            # Token is valid and not revoked.
            uid = decoded_token['uid']
        except auth.RevokedIdTokenError:
            # Token revoked, inform the user to reauthenticate or signOut().
            pass
        except auth.InvalidIdTokenError:
            # Token is invalid
            pass
        print(time.time()-x)
    """
    # clear password
    form.password.data = ''
    return render_template('forms/index.html',
                           form=form,
                           entire_form_errors=entire_form_error,
                           extra_error=extra_error)


@accounts_router.route('/signup', methods=('GET', 'POST'))
def signup() -> Response:
    """
    :return: sign-up user response
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
                'password': User.encrypt_password(pswd, name)
            }
        ))
        if login_error is not None:
            form.email.errors.append(login_error)
        else:
            return render_template('transport/complete-signup.html', username=name)
    return render_template('forms/signup.html', form=form)


@accounts_router.route('/revoke', methods=['GET', 'POST'])
def revoke() -> Response:
    """
    :return: revoke password response
    """
    form = RevokeForm()
    if form.validate_on_submit():
        """
        after user validation checks if the user exists
        """
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            # error handling
            send_revoke_password(
                user.username,
                form.email.data,
                TokenSerializer.revoke.dumps({
                    'email': form.email.data,
                    'password': user.password
                })
            )
            # return template ok
    return render_template('forms/revoke.html', form=form)


@accounts_router.route('/change-password/<string:token>', methods=['GET', 'POST'])
def change_password(token: str) -> Response:
    """
    :param token: token url represent saving url
    :return: Response
    """
    # first get
    extracted = extract_signature(token, is_valid_change_password_token)
    """
    timeout message
    find user
    -- then create the change password form
    -- validate it
    -- then submit
    """
    return None


@accounts_router.route('/logout', methods=('GET', 'POST'))
def logout() -> Response:
    if not current_user.is_anonymous:
        logout_user()
    return redirect(url_for('auth.login'))


@accounts_router.route('/confirm/<string:token>', methods=('GET',))
def confirm(token: str) -> Response:
    extracted = extract_signature(token, is_valid_signup_token)
    if extracted is\
            None:
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
    user = datastore.session.query(User).filter(
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
        email=request.args['name'] + '@gmail.com'
    )
    datastore.session.add(user)
    datastore.session.commit()
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
    datastore.session.add(user)
    datastore.session.commit()
    return redirect(url_for('.login'))
