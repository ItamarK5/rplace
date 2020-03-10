from functools import wraps
from typing import Callable

from flask import abort
from werkzeug import Response

from painter.models.user import User, reNAME
from painter.utils import admin_only
from flask_login import current_user


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
