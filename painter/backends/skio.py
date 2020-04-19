from functools import wraps
from typing import Any, Callable, Optional

from flask_login import current_user
from flask_socketio import SocketIO, disconnect, ConnectionRefusedError

from painter.models import Role


def socket_io_authenticated_only_connection(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    :param f: function to decorate
    :return: wraps the function with another function,
    so the only allows clients that are have already login to connent the namespace
    """
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
    :return: wrapper decorator
    creates new decorater function for the params (read the wrapper for more)
    """
    def wrapper(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """
        :param f: io connection event handler
        :return: wraps f with another function (wrapped) so that only users
        with the role described above
        """
        @wraps(f)
        def wrapped(*args, **kwargs) -> Any:
            """
            :param args: function arguments
            :param kwargs: function arguments
            :return: decorated function
            wraps a io connection event handler function such that prevent any user
            that is role isn't superior to the passed to the function creating the wrapped function
            """
            if not current_user.has_required_status(role):
                raise ConnectionRefusedError(desc) if desc else ConnectionRefusedError()
            else:
                # call app
                return f(*args, **kwargs)

        return socket_io_authenticated_only_connection(wrapped)
    return wrapper


def socket_io_authenticated_only_event(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    :param f: io event handeling
    :return: wrapped function
    wraps the given f with function wrapped, such that bans the user if become not active
    not need to recheck user existing, because already check on connection
    """
    @wraps(f)
    def wrapped(*args, **kwargs) -> Any:
        if not current_user.is_active:
            disconnect('Banned')
        else:
            return f(*args, **kwargs)
    return wrapped


# declaring socketio namespace names
PAINT_NAMESPACE = '/paint'
ADMIN_NAMESPACE = '/admin'

# the socketio object
sio = SocketIO(logger=True)
