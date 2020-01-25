from scripts import *
from flask import Flask, redirect, render_template, abort, send_from_directory, request, url_for, jsonify
from os.path import join as path_join
from flask_login import login_user, LoginManager, login_required


app = Flask(__name__, static_folder='', static_url_path='', template_folder=path_join(WEB_FOLDER))

"""
    initilazetion
"""

app = init_settings(app)
crsf.init_app(app)
db.init_app(app)
login_manager.init_app(app)
app.register_blueprint(auth_router)

def get_rules():
    rules = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        rules.append([
            rule.endpoint, methods
        ])
    return jsonify(rules)


@app.route('/', methods=('GET', ),)
def first():
    return redirect(url_for('auth.login'))


@app.route('/place', methods=('GET',))
@login_required
def place():
    return render_template('place.html')


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
            path_join(WEB_FOLDER, 'static', key.split(".")[-1]), key,
            mimetype=mimetype
        )
    except Exception as e:
        print('error', e)
    abort(404, 'file don\'t found')


@app.route('/favicon.ico', methods=('GET',))
def serve_icon():
    return send_from_directory(
        path_join(WEB_FOLDER, 'static', 'ico'), 'favicon.ico',
        mimetype=MIMETYPES['ico']
    )

