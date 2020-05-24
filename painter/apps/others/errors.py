from typing import Union, Tuple

from flask import request
# noinspection PyProtectedMember
from flask_wtf.csrf import CSRFError
from werkzeug import Response
from werkzeug import exceptions
from werkzeug.exceptions import HTTPException

from .router import other_router
from .utils import is_ajax_request, has_matched_image, render_meme_error_page


@other_router.app_errorhandler(CSRFError)
def handle_csrf_error(e: CSRFError) -> Union[Tuple[Response, int], HTTPException]:
    """
    :param e: csrf error
    :return: csrf error response page if its not a xhr request
    handles CSRF exception
    """
    if not is_ajax_request(request):
        return render_meme_error_page(
            e,
            'csrf',
            'invalid csrf token',
            'Cross-Site-Forgery-Key Error'
        )
    return e


@other_router.app_errorhandler(exceptions.HTTPException)
def error_handler(e: exceptions.HTTPException) -> Union[Tuple[Response, int], HTTPException]:
    """
    :param e: HTTPError raised
    :return: handles normal HTTP Errors
    """
    # if can handle the specific http error by meme image
    if has_matched_image(e) and not is_ajax_request(request):
        return render_meme_error_page(e)
    # else continue raise
    return e
