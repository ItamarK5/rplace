from functools import wraps
from typing import Callable, Optional

from flask import abort, jsonify, request
from flask_login import current_user
from flask_login import fresh_login_required
from werkzeug import Response

from painter.models import Role, User
from painter.others.wtforms_mixins import UsernamePattern


def role_required(role: Role) -> Callable:
    """
    :param role: a minimal role required to enter
    :return: if the user has the required status to enter
    """
    def wrapper(f: Callable) -> Callable:
        """
            :param f: decorator, which decorates a view, make it role only used
            :return: a route that aborts 404 non-admin users that enter, all actions of admin must be with refreshed login
        """
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not (current_user.is_authenticated and current_user.has_required_status(role)):
                # abort 404
                abort(404)
            # else
            else:
                # decorated by flesh_login_required, so that it user isnt refreshed and prevent seeing the site
                return fresh_login_required(f)(*args, **kwargs)
        return wrapped
    return wrapper


def only_if_superior(f: Callable[[User], Response]) -> Callable[[str], Response]:
    """
    :param f: a view which the url get a name parameter represent the name of a user and need to pass a User object
    :return: a wrapped function of the view that prevent the user if not superior to the given user with name
                also passes the user with the name to the function
    check if the user is superior to the user with the name, also passes the user to the function
    """

    @wraps(f)
    def wrapped(*args, **kwargs) -> Response:
        # check user name
        if 'name' in kwargs:
            name = kwargs.pop('name')
        else:
            name = request.args.get('name', None)
            if not isinstance(name, str):
                abort(400)
        if not UsernamePattern.match(name):
            abort(404, 'Cannot access user')
        user = User.query.filter_by(username=name).first()
        if user is None:
            abort(404, 'Cannot access user')  # Not Found
        elif not current_user.is_superior_to(user):
            abort(403, 'Cannot access user')  # Forbidden
        return f(user=user, *args, **kwargs)

    # uses role_reuqired to check if the user is authenticated and at least admin
    return role_required(Role.admin)(wrapped)


def json_response(success: bool, text: str) -> Response:
    """
    :param success: if succeed
    :param text: text of the response
    :return: JSON Response with the params
    """
    return jsonify({
        'success': int(success),
        'text': text
    })


def validate_get_notes_param(arg_name: str) -> Optional[int]:
    """
    :param arg_name: name of arguments holding the number of notes
    :return: the number of notes contained
    can raise BadRequest
    """
    arg = request.args.get(arg_name, 'None')
    if arg.isdigit():  # all digits => int
        return int(arg)
    else:  # else abort Bad Request
        abort(400, 'Un-valid value for page')
    return arg
