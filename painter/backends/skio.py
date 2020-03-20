from functools import wraps
from typing import Any, Callable

from flask_login import current_user
from flask_socketio import SocketIO, disconnect

from painter.models.role import Role


def socket_io_authenticated_only(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
    @wraps(f)
    def wrapped(*args, **kwargs) -> Any:
        print(f)
        if current_user.is_anonymous or not current_user.is_active:
            raise disconnect()
        else:
            return f(*args, **kwargs)

    return wrapped


def socket_io_role_required(role: Role) -> Callable[[Any], Any]:
    """
    :param role: the required role to pass
    :return: the socket.io view, but now only allows if the user is authenticated
    """

    def wrapped(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
        @wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            if not current_user.has_required_status(role):
                disconnect()
            else:
                return f(*args, **kwargs)

        return socket_io_authenticated_only(wrapper)

    return wrapped


# declaring socketio namespace names
PAINT_NAMESPACE = '/paint'
ADMIN_NAMESPACE = '/admin'
PROFILE_NAMESPACE = '/profile'
sio = SocketIO(logger=True)
