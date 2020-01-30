import random
from flask import Blueprint, render_template, send_from_directory, request
from painter.constants import MIME_TYPES, WEB_FOLDER
from os import path, listdir
from painter.functions import get_file_type
from werkzeug.exceptions import HTTPException

meme_router = Blueprint(
    'meme_views',
    'meme_views',
    static_folder=path.join(WEB_FOLDER, 'memes'),
    template_folder=path.join(WEB_FOLDER, 'templates', 'memes')
)


@meme_router.route('/meme/<string:http_error>')
def meme_image(http_error: str):    
    if str(http_error) not in listdir(path.join(meme_router.static_folder)):
        return send_from_directory(path.join(meme_router.static_folder, '404'), 'images.jfif', mimetype=MIME_TYPES.get('jfif', None))
    # else
    # I select the image
    error_path = path.join(meme_router.static_folder, http_error)
    random_meme = random.choice(listdir(error_path))
    return send_from_directory(
        error_path,
        random_meme,
        mimetype=MIME_TYPES[get_file_type(random_meme)],
        cache_timeout=30  # five seconds top save, to prevent fast reloads request
    )


"""
continue returning the memes
needs to solve error and update mimetypes
"""


def error_meme_render(e: HTTPException):
    # future plans, add isinstance string to detect if it's string, security
    if str(e.code) not in listdir(meme_router.static_folder):
        http_error = 'meme not found'
    return render_template('meme.html',
                           error=e.code,
                           title=e.name,
                           description=e.description if e.description is not None else e.name)


@meme_router.app_errorhandler(404)
def error_handler(e):
    if 'text/html' in request.accept_mimetypes:
        return error_meme_render(e)
    return e


@meme_router.route("/<path:arg>")
def default_route(*args):
    return error_meme_render('404', 'File not Found')

