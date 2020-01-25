from flask import blueprint, render_template, send_from_directory
from os import path, listdir
from ..consts import MIMETYPES
import random


TEMPLATE_PATH = path.join(path.split(__file__)[:-2], 'web', 'template', 'meme.html')
IMAGES_MEME_PATH = path.join(path.split(__file__)[:-2], 'web', 'memes')


meme_router = blueprint('errors', __name__, template_folder='..\\web\\memes')

@meme_router.route('/', defaults={'http_error', 'meme'})
@meme_router.route('//meme//<int:http_error>')
def error_meme(http_error):    
    if str(err) not in listdir(MEME_PATH):
        return send_from_directory(path.join(MEME_PATH, '404'), 'images.jfif', mimetype=None)
    # else
    # I select the image
    temp_path = path.join(MEME_PATH, err)
    random_meme = random.choice(listdir(temp_path))  
    return send_from_directory(
        IMAGES_MEME_PATH,
        random_meme,
        MIMETYPES[random_meme.split('.')[-1]],
        cache_timeout=15  # five seconds top save, to prevent fast reloads request
    )
    """
    continue returning the memes
    needs to solve error and update mimetypes
    """

def error_meme(error:str):
    # future plans, add insinstance string to detect if it's string, security
    if err not in listdir(error):
        error = 'meme not found'
    return render_template(MEME_PATH, error=error)


@meme_router.app_errorhandler(404)
def error_handler():
    return error_meme('404')

@meme_router.route('/<path:dummy>')
def fail_to_route(dummy):
    return error_meme('404')