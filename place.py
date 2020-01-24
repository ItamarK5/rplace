from flask import Flask, redirect, render_template, abort, send_from_directory
from scripts.alchemy import init_app as init_alchemy
from scripts.functions import encrypt_password
from scripts.settings import init_app as init_settings
from scripts.forms import *
from os.path import join as path_join

__all__ = ['app.py']
app = Flask(__name__, static_folder='', static_url_path='')
app = init_settings(app)
app = init_alchemy(app)

@app.route('/', methods=('GET', 'POST'),)
def login():
    """
    added in version 1.0.0
    """
    form = LoginForm()
    error_message = None
    if form.validate_on_submit():
        name, pswd = form.username.data, form.password.data
        pswd = encrypt_password(name, pswd)
        user = User.query.filter_by(username=name, password=pswd).first()
        if user is None:
            error_message = 'username or password dont match'
        else:
            return redirect('/place')
    form.password.data = ''
    return render_template('forms/index.html', form=form, message=error_message)

mimetypes = {
    'png': 'image/png',
    'ico': 'image/x-icon',
    'css': 'text/css',
    'js' : 'text/javascript'
}

@app.route('/files/<path:key>', methods=('GET',))
def serve_static(key):
    if key.rfind('.') == -1:
        abort(405, 'unvalid file format')
    # else
    mimetype = mimetypes.get(key.split('.')[-1], None)
    if mimetype is None:
        abort(405, 'type not supported')
    # return file
    try:
        return send_from_directory(
            path_join('static', key.split(".")[-1]), key,
            mimetype=mimetype
        )
    except Exception as e:
        print('error', e)
    abort(404, 'file dont found')