import random
from flask import Blueprint, render_template, send_from_directory
from ..consts import MIMETYPES, WEB_FOLDER
from os import path, listdir


meme_router = Blueprint(
    'meme_views',
    'meme_views',
    static_folder=path.join(WEB_FOLDER, 'memes'),
    template_folder=path.join(WEB_FOLDER, 'templates', 'memes')
)


@meme_router.route('/meme//<string:http_error>')
def error_meme(http_error):    
    if str(http_error) not in listdir(path.join(meme_router.static_folder)):
        return send_from_directory(path.join(meme_router.static_folder, '404'), 'images.jfif', mimetype=None)
    # else
    # I select the image
    temp_path = path.join(meme_router.static_folder, http_error)
    random_meme = random.choice(listdir(temp_path))  
    return send_from_directory(
        meme_router.static_folder,
        random_meme,
        mimetype=MIMETYPES[random_meme.split('.')[-1]],
        cache_timeout=15  # five seconds top save, to prevent fast reloads request
    )

"""
continue returning the memes
needs to solve error and update mimetypes
"""


def error_meme_render(http_error: str):
    # future plans, add insinstance string to detect if it's string, security
    if http_error not in listdir(meme_router.static_folder):
        error = 'meme not found'
    return render_template('meme.html', error=http_error)


@meme_router.app_errorhandler(404)
def error_handler():
    return error_meme_render('404')


@meme_router.app_url_defaults
def default_route(*args):
    print(args)
    return error_meme_render('404')