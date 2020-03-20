from typing import Any

from painter.backends import lock
from painter.backends.skio import (
    sio, ADMIN_NAMESPACE, socket_io_role_required, PAINT_NAMESPACE
)
from painter.models.role import Role


@sio.on('connect', ADMIN_NAMESPACE)
@socket_io_role_required(Role.admin)
def connect():
    pass


@sio.on('change-lock-state', ADMIN_NAMESPACE)
@socket_io_role_required(Role.admin)
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
