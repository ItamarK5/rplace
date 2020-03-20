from typing import Any, Callable, Dict
from painter.models.user import User
from painter.backends import lock
from painter.backends.skio import (
    sio, ADMIN_NAMESPACE,
    PAINT_NAMESPACE, EDIT_PROFILE_NAMESPACE,
    PROFILE_NAMESPACE, emit_namespaces,
    socket_io_role_required_connection, socket_io_role_required_event,
)
from painter.backends.extensions import datastore
from werkzeug.datastructures import MultiDict
from flask import request
from flask_login import current_user
from painter.models.role import Role
from painter.models.notes import Note, Record
from flask_socketio import join_room, ConnectionRefusedError, rooms, disconnect
from .forms import NoteForm, RecordForm
from functools import wraps
from datetime import datetime
from flask import escape, json


def socket_io_require_user_room(f: Callable) -> Callable:
    @wraps(f)

    def wrapper(*args, **kwargs):
        client_rooms = rooms(request.sid)
        for room in client_rooms:
            if room.endswith('-room'):
                name = room.split('-')
                user = User.query.filter_by(username=name).first()
                if user is None:
                    disconnect()
                else:
                    return f(user=user, *args, **kwargs)
            # else
            else:
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
        join_room(f'{username}-room')


@sio.on('add-record', EDIT_PROFILE_NAMESPACE)
@socket_io_role_required_event(Role.admin)
def add_record(user:User, message: Dict[str, str]):
    if not isinstance(message, dict):
        return flask_json.dumps(success=False, error='unvalid inputs')
    for pair in message.items():
        for item in pair:
            if not isinstance(item, str):
                return json.dumps(success=False, error='unvalid inputs')
    form = RecordForm(MultiDict(message))
    if form.validate():
        record = Record(
            user=user.id,
            description=escape(form.note.data),
            declared=datetime.now(),
            writer=current_user.id,
            active=not form.set_banned.data,
            expire=form.expires.data,
            reason=escape(form.reason.data)
        )
        datastore.session.add(record)
        datastore.session.commit()
        user.forget_last_record()
        return {'valid': True}
    # else
    else:
        return {
            'valid': False,
            'errors': dict(
                [(field.name, field.errors) for field in form]
            )
        }
