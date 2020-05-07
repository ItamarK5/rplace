from os import path, listdir
from typing import Optional

from flask import current_app
from flask import render_template, Response
from werkzeug import Request
from werkzeug import exceptions
from werkzeug.exceptions import BadRequest, Forbidden, NotFound, HTTPException, InternalServerError

# a set containing all valid HTTPExceptions that have answer in web\memes except CSRFError
MEME_PAGE_ERROR_CODES = {BadRequest.code, Forbidden.code, NotFound.code, InternalServerError.code}


def has_matched_image(e: HTTPException) -> bool:
	"""
	:param e: e exception
	:return: if the httpException has meme images in the web\memes folder
	"""
	return e.code in MEME_PAGE_ERROR_CODES


def get_file_type(key_file: str) -> Optional[str]:
	"""
	:param key_file: key representing a file in static folder
	:return: the extension name, ideally should be with the name of the file
	"""
	index_start = key_file.rfind('.', -5)  # no file extension above 4 from those I use
	if index_start != -1:
		return key_file[index_start + 1:]
	return None


def is_ajax_request(request: Request) -> bool:
	"""
	:param request: HTTPRequest
	:return: if the request is ajax request
	ajax request have X-Request-With value as XMLHttpRequest
	"""
	# check for ajax XMLRequest
	request_xhr_key = request.headers.get('X-Requested-With')
	# return "is not ajax request"
	# => valid meme request
	return request_xhr_key and request_xhr_key == 'XMLHttpRequest'


def render_meme_error_page(e: exceptions.HTTPException,
                           case: Optional[str] = None, page_title: Optional[str] = None,
                           name: Optional[str] = None) -> Response:
	"""
	:param e: the exception to render the page_error
	:param case: the name of the case for the error/code of the HTTPException
	:param page_title: the title of the page
	:param name: name of the error/default the HTTPException.name
	:return:
	"""
	case = case or str(e.code)
	name = name or str(e.name)
	# recheck
	if case not in listdir(path.join(current_app.root_path,
	                                 'web',
	                                 'memes')):
		return e  # return default error
	else:
		return render_template(
			'responses/meme.html',
			case=case,
			title=name,
			description=e.description or name,
			page_title=case if page_title is None else page_title
		)
