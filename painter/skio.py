from datetime import datetime
from typing import Any, Dict, Callable
from flask_login import current_user
from flask_socketio import SocketIO, Namespace, ConnectionRefusedError, disconnect
from .backends import board, lock
from painter.constants import MINUTES_COOLDOWN
from painter.extensions import datastore
from .models.pixel import Pixel
from functools import wraps
from painter.models.role import Role
import json

TypeCall = Callable[[Any], Any]
sio = SocketIO(logger=True)


def socket_io_authenticated_only(f: TypeCall) -> TypeCall:
    @wraps(f)
    def wrapped(*args, **kwargs) -> Any:
        if current_user.is_anonymous or not current_user.is_active:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


def socket_io_role_required(role: Role) -> TypeCall:
    """
    :param role: the required role to pass
    :return: the socket.io view, but now only allows if the user is authenticated
    """
    def wrapped(f: TypeCall) -> TypeCall:
        @wraps(f)
        def wrapped2(*args, **kwargs) -> Any:
            if current_user.has_required_status(role):
                disconnect()
            else:
                return f(*args, **kwargs)
        return socket_io_authenticated_only(wrapped2)
    return wrapped


class PaintNamespace(Namespace):
    @staticmethod
    def on_connect() -> None:
        """
        :return: nothing
        when connects to PaintNamespace, prevent anonymous users from using SocketIO
        """
        if not current_user.is_authenticated:
            raise ConnectionRefusedError()

    @staticmethod
    @socket_io_authenticated_only
    def on_get_data():
        return {
            'board': board.get_board(),
            'time': str(current_user.next_time),
            'lock': not lock.is_enabled()
        }

    def set_at(self, x: int, y: int, color: int) -> None:
        """
        :param x: valid x coordinate
        :param y: valid y coordinate
        :param color: color of the pixel
        :return: nothing
        sets a pixel on the screen
        -- sets the pixel in the redis server
        -- brodcast to all watchers that the pixel has changed
        """
        board.set_at(x, y, color)
        self.emit('set_board', (x, y, color))
        print(3)

    def pause_place(self) -> None:
        self.emit('pause-board', 0)

    def play_place(self):
        self.emit('pause-board', 1)

    @socket_io_authenticated_only
    def on_set_board(self, params: Dict[str, Any]) -> str:
        """
        :param params: params given to the Dictionary
        :return: string represent the next time the user can update the canvas,
                 or undefined if couldn't update the screen
        """
        # somehow logged out between requests
        try:
            current_time = datetime.utcnow()
            if current_user.next_time > current_time:
                return json.dumps({'code': 'time', 'status': str(current_user.next_time)})
            if not lock.is_enabled():
                return json.dumps({'code': 'lock', 'status': 'true'})
            # validating parameter
            if 'x' not in params or (not isinstance(params['x'], int)) or not (0 <= params['x'] < 1000):
                return 'undefined'
            if 'y' not in params or (not isinstance(params['y'], int)) or not (0 <= params['y'] < 1000):
                return 'undefined'
            if 'color' not in params or (not isinstance(params['color'], int)) or not (0 <= params['color'] < 16):
                return 'undefined'
            next_time = current_time
            current_user.next_time = next_time
            x, y, clr = int(params['x']), int(params['y']), int(params['color'])
            datastore.session.add(
                Pixel(
                    x=x,
                    y=y,
                    color=clr,
                    drawer=current_user.id,
                    drawn=current_time.timestamp()
                )
            )
            datastore.session.commit()
            sio.start_background_task(self.set_at, x=x, y=y, color=clr)
            # setting the board
            """
            if x % 2 == 0:
                board[y, x // 2] &= 0xF0
                board[y, x // 2] |= clr
            else:
                board[y, x // 2] &= 0x0F
                board[y, x // 2] |= clr << 4
            """
            #        board.set_at(x, y, color)
            return json.dumps({'code': 'time', 'value': str(next_time)})
        except Exception as e:
            print(e, e.args)
            return 'undefined'


PAINT_NAMESPACE = PaintNamespace('/paint')
sio.on_namespace(PAINT_NAMESPACE)
