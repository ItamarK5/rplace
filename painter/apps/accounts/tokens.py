from __future__ import absolute_import

from typing import Any, Optional, Union, Dict, Type

from flask import Flask, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from painter.others.constants import DEFAULT_MAX_AGE_USER_TOKEN
from painter.others.wtforms_mixins import QuickForm
from .router import accounts_router


class MailTokens(object):
	"""
		uses the flask configuration
		to generate and convert itsdangerous tokens
	"""
	# https://realpython.com/handling-email-confirmation-in-flask/
	signup: URLSafeTimedSerializer
	revoke: URLSafeTimedSerializer

	@classmethod
	def init_app(cls, app: Flask) -> None:
		"""
		:param app: the Application object
		:return: None
		initialize the token serializer backend with the application configuration
		"""
		cls.signup = URLSafeTimedSerializer(
			secret_key=app.config['SECRET_KEY'],
			salt=app.config['APP_TOKEN_SIGNUP_SALT'],

		)
		cls.revoke = URLSafeTimedSerializer(
			secret_key=app.config['SECRET_KEY'],
			salt=app.config['APP_TOKEN_REVOKE_SALT'],
		)

	@staticmethod
	def get_max_age():
		"""
		:return: the maximum age a token is until it becomes expired
		"""
		return current_app.config.get('APP_MAX_AGE_USER_TOKEN', DEFAULT_MAX_AGE_USER_TOKEN)

	@classmethod
	def extract_signature(
			cls,
			token: str,
			form: Type[QuickForm],
			serializer: URLSafeTimedSerializer) -> Optional[Union[Dict[str, Any], str]]:
		"""
		:param token: token, a string that was encoded by the server represent a user
		:param form:  form to validate if the token is valid
		:param serializer: URLSafeTimedSerializer object that encoded the file before
		:return: None if the token isn't valid
		else returns the timestamp of the token
		"""
		try:
			token = serializer.loads(
				token,
				return_timestamp=True,
				max_age=cls.get_max_age()
			)[0]
		except SignatureExpired:
			return 'timestamp'
		except BadSignature:  # error
			return None
		# then
		# check type
		if not isinstance(token, dict):
			return None
		# check are valid
		form.fast_validation(**token)[0].error_print()
		if not form.are_valid(**token):
			return None
		# else
		return token


@accounts_router.before_app_first_request
def init_tokens() -> None:
	"""
	:return: init the token generator object
	"""
	MailTokens.init_app(current_app)
