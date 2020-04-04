
import random
from os import path, listdir
from typing import Union

from flask import (
    send_from_directory,
    abort, Response, request, current_app
)
from flask_wtf.csrf import CSRFError  # ignore all
from werkzeug.exceptions import HTTPException

from painter.others.constants import MIME_TYPES
from . import other_router
from .utils import get_file_type, has_matched_image, is_ajax_request, render_error_page


@other_router.route('/meme/<string:error>')
def meme_image(error: str) -> Response:
    if str(error) not in listdir(path.join(other_router.static_folder, 'memes')):
        # funny
        abort(404)
    """
        else
        select random image
    """
    error_path = path.join(other_router.static_folder, 'memes', error)
    random_meme = random.choice(listdir(error_path))
    return send_from_directory(
        error_path, random_meme,
        mimetype=MIME_TYPES[get_file_type(random_meme)],
        cache_timeout=1  # five seconds top save, to prevent fast reloads request
    )


@other_router.app_errorhandler(CSRFError)
def handle_csrf_error(e: CSRFError) -> Response:
    """
    :param e: csrf error
    :return: csrf error meme html page if valid meme request
    """
    if not is_ajax_request(request):
        return render_error_page(
            e,
            'csrf',
            'unvalid csrf token',
            'Cross-Site-Forgery-Key Error'
        )
    return e


@other_router.app_errorhandler(HTTPException)
def painter_error_handler(e: HTTPException) -> Union[str, HTTPException]:
    if has_matched_image(e) and not is_ajax_request(request):
        return render_error_page(e)
    return e


@other_router.route('/files/<path:key>', methods=('GET',))
def serve_static(key: str) -> Response:
    file_format = get_file_type(key)
    if not file_format:  # include no item scenerio
        abort(404, 'Forgot placeing file type')
    if file_format not in listdir(path.join(current_app.root_path, 'web', 'static')):
        abort(404, 'unvalid file format')
    # meme type check
    mime_type = MIME_TYPES.get(file_format, None)
    if mime_type is None:
        abort(404, 'type not supported')
    try:
        return send_from_directory(
            path.join(current_app.root_path, 'web', 'static', key.split(".")[-1]),
            key,
            mimetype=mime_type
        )
    except Exception as e:
        print('error', e)
        abort(404, 'file don\'t found')


@other_router.route('/favicon.ico', methods=('GET',))
def serve_icon() -> Response:
    return send_from_directory(
        path.join(current_app.root_path, 'web', 'static', 'ico'),
        'favicon.ico',
        mimetype=MIME_TYPES['ico']
    )
