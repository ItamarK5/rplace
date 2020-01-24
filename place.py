from scripts import *
from flask import Flask, redirect, render_template, abort, send_from_directory, request
from os.path import join as path_join
from flask_login import login_user, LoginManager, login_required
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__, static_folder='', static_url_path='', template_folder='web/templates')
app = init_settings(app)
db.init_app(app)
crsf = CSRFProtect(app)
login_manager.init_app(app)


@app.route('/', methods=('GET', ),)
def first():
    return redirect('login')


@app.route('/login', methods=('GET', 'POST'),)
def login():
    """
    added in version 1.0.0
    """
    form = LoginForm()
    error_message = None
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


@app.route('/signup', methods=('GET', 'POST'))
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
           return redirect('/')
    return render_template('forms/signup.html', form=form)

            
@app.route('/place', methods=('GET',))
@login_required
def place(user_id):
    pass

JOINED_PATH = path_join('web', 'static')
@app.route('/files/<path:key>', methods=('GET',))
def serve_static(key):
    if key.rfind('.') == -1:
        abort(405, 'unvalid file format')
    # else
    mimetype = MIMETYPES.get(key.split('.')[-1], None)
    if mimetype is None:
        abort(405, 'type not supported')
    # return file
    try:
        return send_from_directory(
            path_join(JOINED_PATH, key.split(".")[-1]), key,
            mimetype=mimetype
        )
    except Exception as e:
        print('error', e)
    abort(404, 'file dont found')

