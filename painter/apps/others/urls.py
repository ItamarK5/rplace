import random
from os import path, listdir
from typing import Tuple, Dict, Union, Optional
from flask import (
    Blueprint, render_template, send_from_directory,
    request, abort, Response
)
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException, NotFound

from painter.constants import MIME_TYPES, WEB_FOLDER
from .helpers import get_file_type

other_router = Blueprint(
    'other',
    'other',
    static_folder=path.join(WEB_FOLDER),
)


@other_router.route('/meme/<string:http_error>')
def meme_image(http_error: str) -> Response:
    if str(http_error) not in listdir(path.join(other_router.static_folder, 'memes')):
        # funny
        abort(404)
    """
        else
        select random image
    """
    error_path = path.join(other_router.static_folder, 'memes', http_error)
    random_meme = random.choice(listdir(error_path))
    return send_from_directory(error_path, random_meme,
                               mimetype=MIME_TYPES[get_file_type(random_meme)],
                               cache_timeout=1  # five seconds top save, to prevent fast reloads request
                               )


def error_meme_render(e: HTTPException,
                      case: Optional[str] = None,
                      name: Optional[str] = None) -> Union[str, HTTPException]:
    case = case or str(e.code)
    name = name or str(e.name)
    if case not in listdir(path.join(other_router.static_folder, 'memes')):
        return e    # return default error
    return render_template('memes/meme.html',
                           error=case, title=name,
                           description=e.description or name)


@other_router.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    """
    :param e: csrf error
    :return: csrf error meme view
    """
    return error_meme_render(e, 'csrf', 'Cross-Site-Forgery-Key')


@other_router.app_errorhandler(404)
def error_handler(e: HTTPException) -> Union[str, NotFound]:
    if 'text/html' in request.accept_mimetypes:
        return error_meme_render(e)
    return e


@other_router.app_errorhandler(400)
def error_handler(e: HTTPException) -> Union[str, NotFound]:
    if 'text/html' in request.accept_mimetypes:
        return error_meme_render(e)
    return e


@other_router.route('/files/<path:key>', methods=('GET',))
def serve_static(key: str) -> Response:
    file_format = get_file_type(key)
    if not file_format:  # include no item scenerio
        abort(404, 'Forgot placeing file type')
    if file_format not in listdir(path.join(other_router.static_folder, 'static')):
        abort(404, 'unvalid file format')
    # meme type check
    mime_type = MIME_TYPES.get(file_format, None)
    if mime_type is None:
        abort(404, 'type not supported')
    try:
        return send_from_directory(
            path.join(other_router.static_folder, 'static', key.split(".")[-1]),
            key,
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