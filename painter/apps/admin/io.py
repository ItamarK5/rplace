"""
admin urls staff
"""
from functools import wraps
from typing import Any, Callable

from flask import request
from flask_socketio import ConnectionRefusedError, rooms, disconnect

from painter.backends.skio import (
    sio, ADMIN_NAMESPACE,
    socket_io_role_required_connection,
)
from painter.models import Role, User


@sio.on('connect', ADMIN_NAMESPACE)
@socket_io_role_required_connection(Role.admin)
def connect() -> None:
    """
    just apply decorators to prevent no admin users to access this pages
    """
    pass
