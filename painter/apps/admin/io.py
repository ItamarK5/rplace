from typing import Any
from painter.models.user import User
from painter.backends import lock
from painter.backends.skio import (
    sio, ADMIN_NAMESPACE,
    PAINT_NAMESPACE, EDIT_PROFILE_NAMESPACE,
    PROFILE_NAMESPACE, emit_namespaces,
    socket_io_role_required_connection, socket_io_role_required_event,
)
from painter.models.role import Role
from flask_socketio import join_room, ConnectionRefusedError, rooms
from .forms import NoteForm, RecordForm

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
def connect(query: str):
    user = User.query.filter_by(query).first()
    if user is None or user.is_superior_to(query):
        raise ConnectionRefusedError()
    join_room(f'{query}-room')


@sio.on('add-note', EDIT_PROFILE_NAMESPACE)
@socket_io_role_required_event(Role.admin)
def set_preference(form_args):
    print(form_args)
    if form_args is None:
        return None