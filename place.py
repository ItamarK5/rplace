from scripts import *
from flask import Flask, redirect, render_template, abort, send_from_directory, request
from os.path import join as path_join
from flask_login import login_user, LoginManager, login_required
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__, static_folder='', static_url_path='', template_folder='web/templates')
"""
    initilazetion
"""

app = init_settings(app)
crsf.init_app(app)
db.init_app(app)
login_manager.init_app(app)


@app.route('/', methods=('GET', ),)
def first():
    return redirect('login')



@app.route('/place', methods=('GET',))
@login_required
def place():
    return render_template('place.html')


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


@app.route('/favicon.ico', methods=('GET',))
def serve_icon():
    return send_from_directory(
        path_join(JOINED_PATH, 'ico'), 'favicon.ico',
        mimetype=MIMETYPES['ico']
    )

