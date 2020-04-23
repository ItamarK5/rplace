"""
    Name: utils.py
    Auther: Itamar Kanne
    utilies for mostly the manager.py
"""
from __future__ import absolute_import

from typing import (
    Optional, TypeVar, List,
    Union, FrozenSet, Iterable,
    Type, Dict, Any
)

import click
from flask import redirect, request
from werkzeug import Response

from .constants import (
    FLAG_SERVICES_OPTIONS
)
from .wtforms_mixins import (
    NewUsernameFieldMixin,
    NewEmailFieldMixin,
    QuickForm
)

ConvertType = TypeVar('ConvertType', int, bool, float)


class QuickEmailForm(
    QuickForm,
    NewEmailFieldMixin
):
    pass


class QuickUsernameForm(
    QuickForm,
    NewUsernameFieldMixin
):
    pass


class QuickPasswordForm(
    QuickForm,
    NewUsernameFieldMixin
):
    pass


class FormValidateType(click.ParamType):
    """
    Utility class to use wtforms validators to validate flask.cli values
    """

    def __init__(self, field: str, form: Type[QuickForm]) -> None:
        """
        :param field: the name of the field parrssed by the form
        :param form: a QuickForm that parses 1 field
        """
        super().__init__()
        self.__field = field
        self.__form = form

    def convert(self, value: str, param: str, ctx: click.Context) -> str:
        """
        :param value: value passed to click option
        :param param: the parameter name
        :param ctx: context of flask.cli
        :return: the same value after validating it
        "converts" validates a option passed
        """
        form, is_valid = self.__form.fast_validation(**{self.__field: value})
        if not is_valid:
            # show just first error, it would be enought
            self.fail(form.errors[0], param, ctx)
        return value


def has_service_option(flags: Union[List[str]], all_flag: bool, *options: Iterable[str]) -> bool:
    """
    :param flags: the service flags passed
    :param all_flag: flag
    :param options: list of options for a option for check-services
    :return: if the option service enabled
    """
    if all_flag:
        return True
    if flags is None:
        return False
    # other option flag is empty
    elif not flags:
        return True
    for option in options:
        if option in flags:
            return True
    return False


def parse_service_options(flags: Optional[List[str]], all_flag: bool) -> FrozenSet[str]:
    """
    :param flags: the raw services flags options the user gave
    :param all_flag: flag selecting all options
    :return: the flags as set of values the all the values there represent setted flags
    """
    return frozenset(
        option
        for option in FLAG_SERVICES_OPTIONS
        if has_service_option(flags, all_flag, *FLAG_SERVICES_OPTIONS[option])
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


def abort_if_false(ctx: click.Context, param: str, value:bool):
    """
    :param ctx: context
    :param param: parameter name
    :param value: value of the parameter
    :return: nothing
    aborts the command if value is false
    https://click.palletsprojects.com/en/7.x/options/#yes-parameters
    """
    if not value:
        ctx.abort()


def prompt_are_you_sure(ctx: click.Context, message: Optional[str] = None):
    message = message if message else "Are you sure you want to do this?"
    are_you_sure = click.prompt(type=click.types.BOOL)
    if not are_you_sure:
        return ctx.abort()


class ChoiceMap(click.types.Choice):
    def __init__(self, choices: Dict[Any, str]) -> None:
        # choices aren't case insensitive
        self._map_choices = choices
        # use tuple as said in docs
        super().__init__(choices=tuple(self._map_choices.keys()), case_sensitive=False)

    def convert(self, value: str, param: str, ctx: click.Context) -> str:
        answer_key = super().convert(value, param, ctx)
        # returns the mapped value
        try:
            return self._map_choices[answer_key]
        except KeyError:
            # same as choice
            self.fail(
                "Meet Some Stupid Errro with getting the key",
                param, ctx
            )
