"""
admin urls staff with socketio
"""
from painter.backends.skio import (
	sio, ADMIN_NAMESPACE,
	socket_io_role_required_connection,
)
from painter.models import Role


@sio.on('connect', ADMIN_NAMESPACE)
@socket_io_role_required_connection(Role.admin)
def connect() -> None:
	"""
	just apply decorators to prevent no admin users to access this pages
	"""
	pass
