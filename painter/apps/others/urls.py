import random
from os import path, listdir
from typing import Union

from flask import (
    Blueprint, render_template, send_from_directory,
    request, abort, Response
)
from werkzeug.exceptions import HTTPException, NotFound

from painter.constants import MIME_TYPES, WEB_FOLDER
from .helpers import get_file_type

other_router = Blueprint(
    'other',
    'other',
    static_folder=path.join(WEB_FOLDER),
    template_folder=path.join(WEB_FOLDER, 'templates', 'memes')
)


@other_router.route('/meme/<string:http_error>')
def meme_image(http_error: str) -> Response:
    if str(http_error) not in listdir(path.join(other_router.static_folder, 'memes')):
        return send_from_directory(path.join(other_router.static_folder, '404'), 'images.jfif',
                                   mimetype=MIME_TYPES.get('jfif', None))
    # else
    # select random matches image
    error_path = path.join(other_router.static_folder, 'memes', http_error)
    random_meme = random.choice(listdir(error_path))
    return send_from_directory(
        error_path,
        random_meme,
        mimetype=MIME_TYPES[get_file_type(random_meme)],
        cache_timeout=1  # five seconds top save, to prevent fast reloads request
    )


"""
continue returning the memes
needs to solve error and update mimetypes
"""


def error_meme_render(e: HTTPException) -> str:
    # future plans, add isinstance string to detect if it's string, security
    if str(e.code) not in listdir(other_router.static_folder):
        http_error = 'meme not found'
    return render_template('meme.html',
                           error=e.code,
                           title=e.name,
                           description=e.description if e.description is not None else e.name)


@other_router.app_errorhandler(404)
def error_handler(e: NotFound) -> Union[str, NotFound]:
    if 'text/html' in request.accept_mimetypes:
        return error_meme_render(e)
    return e


@other_router.route('/files/<path:key>', methods=('GET',))
def serve_static(key: str) -> Response:
    file_format = get_file_type(key)
    if not file_format:  # include no item scenerio
        abort(405, 'Forgot placeing file type')
    if file_format not in listdir(path.join(other_router.static_folder, 'static')):
        abort(405, 'unvalid file format')
    # else
    mime_type = MIME_TYPES.get(file_format, None)
    if mime_type is None:
        abort(405, 'type not supported')
    # return file
    try:
        return send_from_directory(
            path.join(
                other_router.static_folder,
                'static', key.split(".")[-1]), key,
            mimetype=mime_type
        )
    except Exception as e:
        print('error', e)
    abort(404, 'file don\'t found')


@other_router.route('/favicon.ico', methods=('GET',))
def serve_icon() -> Response:
    return send_from_directory(
        path.join(other_router.static_folder, 'static', 'ico'), 'favicon.ico',
        mimetype=MIME_TYPES['ico']
    )
