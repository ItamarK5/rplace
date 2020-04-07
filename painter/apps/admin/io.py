from functools import wraps
from typing import Any, Callable

from flask import request
from flask_login import current_user
from flask_socketio import join_room, ConnectionRefusedError, rooms, disconnect

from painter.backends import lock
from painter.backends.skio import (
    sio, ADMIN_NAMESPACE,
    PAINT_NAMESPACE, EDIT_PROFILE_NAMESPACE,
    socket_io_role_required_connection, socket_io_role_required_event,
)
from painter.models import Role, User


def socket_io_require_user_room(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args, **kwargs):
        client_rooms = rooms(request.sid)
        for room in client_rooms:
            if room.startswith('room-'):
                name = room.split('-')[1]
                user = User.query.filter_by(username=name).first()
                if user is None:
                    disconnect()
                else:
                    return f(user, *args, **kwargs)
        # else if not found
        raise ConnectionRefusedError()
    return wrapper


@sio.on('connect', ADMIN_NAMESPACE)
@socket_io_role_required_connection(Role.admin)
def connect():
    pass


@sio.on('change-lock-state', ADMIN_NAMESPACE)
@socket_io_role_required_event(Role.admin)
def change_lock_state(new_state: Any):
    if not isinstance(new_state, bool):
        return {'success': False, 'response': 'Not A Valid Input'}
    # prevent collision
    if lock.set_switch(new_state):
        sio.emit('change-lock-state', new_state, namespace=PAINT_NAMESPACE)
        sio.emit('set-lock-state', new_state, namespace=ADMIN_NAMESPACE, include_self=False)
        return {'success': True, 'response': new_state}
    else:
        return {'success': True, 'response': new_state}


@sio.on('connect', EDIT_PROFILE_NAMESPACE)
@socket_io_role_required_connection(Role.admin)
def connect():
    pass


@sio.on('join', EDIT_PROFILE_NAMESPACE)
@socket_io_role_required_event(Role.admin)
def join_profile(username: str):
    if not isinstance(username, str):
        disconnect()
    user = User.query.filter_by(username=username).first()
    print(user)
    if user is None or not current_user.is_superior_to(user):
        disconnect()
    else:
        join_room(f'room-{username}')