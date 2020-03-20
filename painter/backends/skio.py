from functools import wraps
from typing import Any, Callable, Optional, Iterable

from flask_login import current_user
from flask_socketio import SocketIO, disconnect, ConnectionRefusedError

from painter.models.role import Role


def socket_io_authenticated_only_connection(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
    @wraps(f)
    def wrapped(*args, **kwargs) -> Any:
        if current_user.is_anonymous or not current_user.is_active:
            disconnect('Not Authenticated')
        else:
            return f(*args, **kwargs)

    return wrapped


def socket_io_role_required_connection(role: Role, desc: Optional[str] = None) -> Callable[[Any], Any]:
    """
    :param desc: additional description of the error
    :param role: the required role to pass
    :return: the socket.io view, but now only allows if the user is authenticated
    """

    def wrapped(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
        @wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            if not current_user.has_required_status(role):
                raise ConnectionRefusedError(desc) if desc else ConnectionRefusedError()
            else:
                return f(*args, **kwargs)

        return socket_io_authenticated_only_connection(wrapper)
    return wrapped


def socket_io_authenticated_only_event(f:Callable[[Any], Any]) -> Callable[[Any], Any]:
    @wraps(f)
    def wrapped(*args, **kwargs) -> Any:
        if not current_user.is_active:
            raise disconnect('Banned')
        else:
            return f(*args, **kwargs)
    return wrapped


def socket_io_role_required_event(role: Role, desc: Optional[str] = None) -> Callable[[Any], Any]:
    """
    :param desc: additional description of the error
    :param role: the required role to pass
    :return: the socket.io view, but now only allows if the user is authenticated
    """

    def wrapped(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
        @wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            if not current_user.has_required_status(role):
                raise ConnectionRefusedError(desc) if desc else ConnectionRefusedError()
            else:
                return f(*args, **kwargs)
        return socket_io_authenticated_only_connection(wrapper)
    return wrapped


def emit_namespaces(namespaces: Iterable[str], *args, **kwargs) -> None:
    for ns in namespaces:
        sio.emit(*args, namespaces=ns, **kwargs)


# declaring socketio namespace names
PAINT_NAMESPACE = '/paint'
ADMIN_NAMESPACE = '/admin'
PROFILE_NAMESPACE = '/profile'
EDIT_PROFILE_NAMESPACE = '/edit-profile'
sio = SocketIO(logger=True)
