from functools import wraps
from typing import Callable

from flask import abort
from flask_login import current_user
from flask_login import fresh_login_required
from werkzeug import Response

from painter.models.user import User, reNAME
from painter.models.role import Role


def admin_only(f: Callable) -> Callable:
    """
    :param f: decorator, which decorates a view, make it admin only used
    :return: a route that aborts 404 non-admin users that enter, all actions of admin must be with refreshed login
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.is_authenticated and current_user.has_required_status(Role.admin):
            # decorated by flesh_login_required, so that it user isnt refreshed and prevent seeing the site
            return fresh_login_required(f)(*args, **kwargs)
        # else
        abort(404)

    return wrapped


def only_if_superior(f: Callable[[User], Response]) -> Callable[[str], Response]:
    """
    :param f: a view which the url get a name parameter represent the name of a user and need to pass a User object
    :return: a wrapped function of the view that prevent the user if not suprier to the given user with name
                also passes the user with the name to the function
    check if the user is superier to the user with the name, also passes the user to the function
    """

    @wraps(f)
    def wrapped(name: str, *args, **kwargs) -> Response:
        # check user name
        if not reNAME.match(name):
            abort(404, 'Cannot access user')
        user = User.query.filter_by(username=name).first()
        if user is None:
            abort(404, 'Cannot access user')  # Not Found
        elif not current_user.is_superior_to(user):
            abort(403, 'Cannot access user')  # Forbidden
        return f(user=user, *args, **kwargs)
    return admin_only(wrapped)      # uses admin_only to check if the user is authenticated and at least admin
