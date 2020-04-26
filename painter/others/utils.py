"""
    Name: utils.py
    Auther: Itamar Kanne
    utilies for mostly the manager.py
"""
from __future__ import absolute_import
from werkzeug.routing import Rule
import urllib.parse
from typing import Optional, TypeVar, List, Union, FrozenSet
from flask import current_app
from flask import redirect, request
from flask_script.commands import Command
from werkzeug import Response


from .constants import (
    FLAG_SERVICES_OPTIONS
)
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


def has_service_option(flags: Union[bool, List[str]], *options) -> bool:
    """
    :param flags: the service flags passed
    :param options: list of options for a option for check-services
    :return: if the option service enabled
    """
    if not isinstance(flags, list):
        return flags
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


def find_rule(url:str, method:str) ->  Optional[Rule]:
    for rule in current_app.url_map.iter_rules():
        if rule.match(url, method):
            return rule
    # else
    return None

def is_url_safe(url: str) -> bool:
    """
    :param url: url
    :return: if the url is safe
    """
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.hostname is not None:
        return False
    if parsed_url.port == 80:
        return True

def redirect_next(fallback: str) -> Response:
    """
    :param fallback: fallback path
    :return: response to redirect the user via the next argument
    """
    next_url = request.args.get('next', None)
    if next_url is not None:
        # check in same domain
    return redirect(fallback)
