"""
    Name: utils.py
    Auther: Itamar Kanne
    utilies for mostly the manager.py
"""
from __future__ import absolute_import

from typing import Optional, TypeVar

from flask import current_app
from flask import redirect, request
from flask_script.commands import Command
from werkzeug import Response
from werkzeug.routing import Rule

from .wtforms_mixins import (
    NewUsernameFieldMixin,
    PasswordFieldMixin,
    NewEmailFieldMixin,
    QuickForm
)

ConvertType = TypeVar('ConvertType', int, bool, float)


class NewUserForm(
	QuickForm,
	NewUsernameFieldMixin,
	PasswordFieldMixin,
	NewEmailFieldMixin,
):
	"""
	simple class to validate new user data
	its email address, its name and its password
	"""
	pass


class MyCommand(Command):
	"""
		simple command but with options to describe itself,
	"""
	# class help and class_description are utility for commands
	class_help: Optional[str] = None
	class_description: Optional[str] = None

	def __init__(self, func=None,
	             description: Optional[str] = None,
	             help_text: Optional[str] = None):
		super().__init__(func)
		self.__description = description if description is not None else self.class_description
		self.__help_text = help_text if help_text is not None else self.class_help
		self.__help_text = help_text
		self.option_list = []

	@property
	def description(self) -> str:
		"""
		:return: description of command
		"""
		desc = self.__description if self.__description is not None else ''
		return desc.strip()

	@property
	def help(self) -> str:
		"""
		:return: help text of command
		"""
		help_text = self.__help_text if self.__help_text is not None else self.__description
		return help_text.strip()

	def run(self):
		super().run()


def auto_redirect(url: str) -> Response:
	"""
	:param url: to redirect the user accessing the page
	:return: 302 Response : Redirect to the page
	"""

	# a decoy function
	def view_func():
		return redirect(url)

	if not isinstance(url, str):
		raise TypeError("Url must be string for redirecting")
	# then check if valid
	return view_func


def find_rule(url: str, method: str) -> Optional[Rule]:
	for rule in current_app.url_map.iter_rules():
		if rule.match(url, method):
			return rule
	# else
	return None


def redirect_next(fallback: str) -> Response:
	"""
	:param fallback: fallback path
	:return: response to redirect the user via the next argument
	"""
	next_url = request.args.get('next', None)
	if next_url is not None:
		# check in same domain
		return redirect(next_url)
	return redirect(fallback)
