from flask import Blueprint, render_template, abort, send_from_directory
from os.path import join as path_join
from os import listdir
from painter.constants import MIME_TYPES, WEB_FOLDER
from painter.functions import get_file_type
from flask_login import login_required

place_router = Blueprint('other', 'other',
                         static_folder=path_join(WEB_FOLDER, 'static'),
                         template_folder=path_join(WEB_FOLDER, 'templates'))


@place_router.route('/place', methods=('GET',))
@login_required
def place():
    return render_template('place.html')


@place_router.route('/files/<path:key>', methods=('GET',))
def serve_static(key):
    file_format = get_file_type(key)
    if not file_format:  # include no item scenerio
        abort(405, 'Forgot placeing file type')
    if file_format not in listdir(place_router.static_folder):
        abort(405, 'unvalid file format')
    # else
    mime_type = MIME_TYPES.get(file_format, None)
    if mime_type is None:
        abort(405, 'type not supported')
    # return file
    try:
        return send_from_directory(
            path_join(
                place_router.static_folder,
                key.split(".")[-1]), key,
            mimetype=mime_type
        )
    except Exception as e:
        print('error', e)
    abort(404, 'file don\'t found')


@place_router.route('/favicon.ico', methods=('GET',))
def serve_icon():
    return send_from_directory(
        path_join(place_router.static_folder, 'ico'), 'favicon.ico',
        mimetype=MIME_TYPES['ico']
    )
