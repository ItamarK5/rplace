from flask import Blueprint, render_template, abort, send_from_directory
from os.path import join as path_join
from os import listdir
from ..consts import WEB_FOLDER, MIMETYPES
from flask_login import login_required

other_router = Blueprint('other', 'other',
                         static_folder=path_join(WEB_FOLDER, 'static'),
                         template_folder=path_join(WEB_FOLDER, 'templates'))


@other_router.route('/place', methods=('GET',))
@login_required
def place():
    return render_template('place.html')


@other_router.route('/files/<path:key>', methods=('GET',))
def serve_static(key):
    if key in listdir(other_router.static_folder):
        abort(405, 'unvalid file format')
    # else
    mimetype = MIMETYPES.get(key.split('.')[-1], None)
    if mimetype is None:
        abort(405, 'type not supported')
    # return file
    try:
        return send_from_directory(
            path_join(
                other_router.static_folder,
                key.split(".")[-1]), key,
            mimetype=mimetype
        )
    except Exception as e:
        print('error', e)
    abort(404, 'file don\'t found')


@other_router.route('/favicon.ico', methods=('GET',))
def serve_icon():
    return send_from_directory(
        path_join(other_router.static_folder, 'ico'), 'favicon.ico',
        mimetype=MIMETYPES['ico']
    )
