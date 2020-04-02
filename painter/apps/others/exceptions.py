from typing import Union, Optional
from flask import request, render_template
from typing import Optional
from werkzeug import exceptions
from werkzeug import Response
from flask_wtf.csrf import CSRFError
from . import other_router
from .utils import is_ajax_request, has_matched_image, render_error_page


@other_router.app_errorhandler(CSRFError)
def handle_csrf_error(e: CSRFError) -> Response:
    """
    :param e: csrf error
    :return: csrf error response page if its not a xhr request
    """
    if not is_ajax_request(request):
        return render_error_page(
            e,
            'csrf',
            'unvalid csrf token',
            'Cross-Site-Forgery-Key Error'
        )
    return e


@other_router.app_errorhandler(exceptions.HTTPException)
def error_handler(e: exceptions.HTTPException) -> Union[str, exceptions.HTTPException]:
    if has_matched_image(e) and not is_ajax_request(request):
        return render_error_page(e)
    return e
