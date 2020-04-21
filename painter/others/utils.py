"""
    Name: utils.py
    Auther: Itamar Kanne
    utilies for mostly the manager.py
"""
from __future__ import absolute_import

from abc import ABC
from typing import Optional, TypeVar, List, Union, FrozenSet

from flask import redirect, request
from flask_script.commands import Command
from werkzeug import Response
from wtforms import StringField
from wtforms.validators import ValidationError

from .constants import (
    FLAG_SERVICES_OPTIONS
)
from .wtforms_mixins import (
    UsernameFieldMixin,
    PasswordFieldMixin,
    MailAddressFieldMixin,
    QuickForm
)
from ..models.user import User

ConvertType = TypeVar('ConvertType', int, bool, float)


class NewUserForm(
    QuickForm,
    UsernameFieldMixin,
    PasswordFieldMixin,
    MailAddressFieldMixin,
):
    """
    simple class to validate new user data
    its email address, its name and its password
    """
    def validate_mail_address(self, field: StringField) -> None:
        """
        :param field:  username field
        :return: validates if the mail address isn't already existing with the name
        """
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('User with the mail address already exists')

    def validate_username(self, field: StringField) -> None:
        """
        :param field:  username field
        :return: validate if the name isn't already existing with the name
        """
        if User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError('User with the username already exists')


class MyCommand(Command, ABC):
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


def has_service_option(flags: Optional[List[str]], *options) -> bool:
    if not isinstance(flags, list):
        return False
    # other option flag is empty
    elif not flags:
        return True
    for option in options:
        if option in flags:
            return True
    return False


def parse_service_options(flags: Union[bool, List[str]]) -> FrozenSet[str]:
    """
    :param flags: the raw services flags options the user gave
    :return: the flags as set of values the all the values there represent setted flags
    """
    return frozenset(
        option
        for option in FLAG_SERVICES_OPTIONS
        if has_service_option(flags, FLAG_SERVICES_OPTIONS[option])
    )


def check_service_flag(service_flag: Optional[bool], all_flag: bool) -> bool:
    """
    :param service_flag: if entered the flag of the service
    :param all_flag: if the check all flag passed
    :return the value of the all flag if the user didnt passed an service flag but
    if he d'idnt passed its the value that dont match to all flag
    """
    return all_flag if service_flag is None else service_flag ^ all_flag


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


def redirect_to(fallback: str) -> Response:
    """
    :param fallback: fallback path
    :return: response to redirect the user via the next argument
    """
    url_dest = request.args.get('next', None)
    if url_dest:
        return redirect(url_dest)
    return redirect(fallback)
