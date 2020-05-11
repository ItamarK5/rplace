from __future__ import absolute_import

import random
from os import path, listdir

from flask import (
	send_from_directory,
	abort, Response, current_app
)

from painter.others.constants import MIME_TYPES
from .router import other_router
from .utils import get_file_type


@other_router.route('/meme/<string:error>')
def meme_image(error: str) -> Response:
	"""
	:param error: the number of the error in string
	:return: Image response
	"""
	if str(error) not in listdir(path.join(current_app.root_path, 'web', 'memes')):
		# funny
		abort(404)
	# else select random image
	error_path = path.join(current_app.root_path, 'web', 'memes', error)
	random_meme = random.choice(listdir(error_path))
	return send_from_directory(
		error_path, random_meme,
		mimetype=MIME_TYPES[get_file_type(random_meme)],
		cache_timeout=5  # five seconds top save, to prevent fast reloads request
	)


@other_router.route('/files/<path:filename>', methods=('GET',))
def serve_static(filename: str) -> Response:
	"""
	:param filename: key representing a file name
	:return: the resource file name, if don't exists returns 404
	"""
	file_format = get_file_type(filename)
	if not file_format:  # include no item scenario
		abort(404, 'invalid file format')
	if file_format not in listdir(path.join(current_app.root_path, 'web', 'static')):
		abort(404, 'invalid file format')
	# meme type check
	mime_type = MIME_TYPES.get(file_format, None)
	if mime_type is None:
		abort(404, 'invalid file format')
	try:
		return send_from_directory(
			path.join(current_app.root_path, 'web', 'static', filename.split(".")[-1]),
			filename,
			mimetype=mime_type
		)
	except FileNotFoundError:
		abort(404, 'file don\'t found')


@other_router.route('/favicon.ico', methods=('GET',))
def serve_icon() -> Response:
	"""
	:return: serves the icon of the server
	"""
	return serve_static('favicon.ico')
