import random
from flask import Blueprint, render_template, send_from_directory
from ..consts import MIME_TYPES, WEB_FOLDER
from os import path, listdir


meme_router = Blueprint(
    'meme_views',
    'meme_views',
    static_folder=path.join(WEB_FOLDER, 'memes'),
    template_folder=path.join(WEB_FOLDER, 'templates', 'memes')
)


@meme_router.route('/meme//<string:http_error>')
def meme_image(http_error: str):    
    if str(http_error) not in listdir(path.join(meme_router.static_folder)):
        return send_from_directory(path.join(meme_router.static_folder, '404'), 'images.jfif', mimetype=None)
    # else
    # I select the image
    temp_path = path.join(meme_router.static_folder, http_error)
    random_meme = random.choice(listdir(temp_path))  
    return send_from_directory(
        meme_router.static_folder,
        random_meme,
        mimetype=MIME_TYPES[random_meme.split('.')[-1]],
        cache_timeout=15  # five seconds top save, to prevent fast reloads request
    )

"""
continue returning the memes
needs to solve error and update mimetypes
"""


def error_meme_render(http_error: str, reason: str):
    # future plans, add insinstance string to detect if it's string, security
    if http_error not in listdir(meme_router.static_folder):
        http_error = 'meme not found'
    return render_template('meme.html', error=http_error, title=http_error, reason=reason)


@meme_router.app_errorhandler(404)
def error_handler(reason='File not Found'):
    return error_meme_render('404', reason)


@meme_router.route("/<path:arg>")
def default_route(*args):
    return error_meme_render('404', 'File not Found')

