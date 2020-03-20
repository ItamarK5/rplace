from typing import Optional
from werkzeug import Request
from werkzeug.exceptions import BadRequest, Forbidden, NotFound, HTTPException
MEME_PAGE_ERROR_CODES = {BadRequest.code, Forbidden.code, NotFound.code}


def has_meme_images(e: HTTPException) -> bool:
    return e.code in MEME_PAGE_ERROR_CODES


def get_file_type(file_path: str) -> Optional[str]:
    index_start = file_path.rfind('.', -5)  # no file extension above 4 from those I use
    if index_start != -1:
        return file_path[index_start + 1:]
    return None


def is_valid_meme_request(request: Request) -> bool:
    if 'text/html' not in request.accept_mimetypes:
        return False
    # check for ajax XMLRequest
    request_xhr_key = request.headers.get('X-Requested-With')
    # return "is not ajax request"
    # => valid meme request
    return not(request_xhr_key and request_xhr_key == 'XMLHttpRequest')