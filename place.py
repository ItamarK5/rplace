from flask import Flask, redirect, render_template, abort, send_from_directory
from scripts.alchemy import init_app as init_alchemy
from scripts.functions import encrypt_password
from scripts.settings import init_app as init_settings
from scripts.forms import *
from os.path import join as path_join

__all__ = ['app.py']
app = Flask(__name__, static_folder='static', static_url_path='')
app = init_settings(app)
app = init_alchemy(app)

@app.route('/', methods=('GET', 'POST'),)
def login():
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

@app.route('/files/<string:key>')
def serve_static(key):
    return send_from_directory(path_join('static', key.split('.')[-1]),key)