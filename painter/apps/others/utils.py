from . import other_router
from os import path, listdir
from typing import Optional
from flask import render_template, Response
from werkzeug import Request
from werkzeug import exceptions
from werkzeug.exceptions import BadRequest, Forbidden, NotFound, HTTPException
from flask import current_app

MEME_PAGE_ERROR_CODES = {BadRequest.code, Forbidden.code, NotFound.code}


def has_matched_image(e: HTTPException) -> bool:
    return e.code in MEME_PAGE_ERROR_CODES


def get_file_type(file_path: str) -> Optional[str]:
    index_start = file_path.rfind('.', -5)  # no file extension above 4 from those I use
    if index_start != -1:
        return file_path[index_start + 1:]
    return None


def is_ajax_request(request: Request) -> bool:
    # check for ajax XMLRequest
    request_xhr_key = request.headers.get('X-Requested-With')
    # return "is not ajax request"
    # => valid meme request
    return request_xhr_key and request_xhr_key == 'XMLHttpRequest'


def render_error_page(e: exceptions.HTTPException,
                      case: Optional[str] = None, page_title: Optional[str] = None,
                      name: Optional[str] = None) -> Response:
    case = case or str(e.code)
    name = name or str(e.name)
    if case not in listdir(path.join(current_app.root_path,
                                     'web',
                                     'memes')):
        return e  # return default error
    else:
        return render_template(
            'memes/meme.html',
            case=case,
            title=name,
            description=e.description or name,
            page_title=case if page_title is None else page_title
        )
