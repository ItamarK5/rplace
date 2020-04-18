import json
from datetime import datetime
from typing import Any

from flask_login import current_user
from painter.others.constants import COLOR_COOLDOWN
from painter.backends import lock, board
from painter.backends.extensions import datastore
from painter.backends.skio import (
    sio, PAINT_NAMESPACE,
    socket_io_authenticated_only_connection,
    socket_io_authenticated_only_event,
)


def task_set_board(x: int, y: int, color: int) -> None:
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
    sio.emit('set-board', (x, y, color), namespace=PAINT_NAMESPACE)


@sio.on('connect', PAINT_NAMESPACE)
@socket_io_authenticated_only_connection
def connect():
    """
    :return: suppose to do thing, just reject any connection from users
    """
    pass


@sio.on('get-starter', PAINT_NAMESPACE)
@socket_io_authenticated_only_event
def get_start_data():
    """
    :return: the start data of the user {
    board in pixels:bytes,
    time: the next time the user can update the board,
    lock: if the board is locked
    }
    """
    print(lock.is_open())
    return {
        'board': board.get_board(),
        'time': str(current_user.next_time),
        'lock': not lock.is_open()
    }


@sio.on('set-board', PAINT_NAMESPACE)
@socket_io_authenticated_only_event
def set_board(params: Any) -> str:
    """
    :param params: params given to the Dictionary
    :return: string represent the next time the user can update the canvas,
             or undefined if couldn't update the screen
    """
    # try
    try:
        # get current_time in utc
        current_time = datetime.utcnow()
        # if the still cant update the board
        if current_user.next_time > current_time:
            return json.dumps({'code': 'time', 'status': str(current_user.next_time)})
        # if the board is locked
        if not lock.is_open():
            return json.dumps({'code': 'lock', 'status': 'true'})
        # validating parameter
        if 'x' not in params or (not isinstance(params['x'], int)) or not (0 <= params['x'] < 1000):
            return 'undefined'
        if 'y' not in params or (not isinstance(params['y'], int)) or not (0 <= params['y'] < 1000):
            return 'undefined'
        if 'color' not in params or (not isinstance(params['color'], int)) or not (0 <= params['color'] < 16):
            return 'undefined'
        # the data is valid, so emit the response
        # update next time
        next_time = current_time + COLOR_COOLDOWN
        current_user.next_time = next_time
        # update current_user in the SQL Database
        datastore.session.add(current_user)
        datastore.session.commit()
        # get data
        x, y, clr = int(params['x']), int(params['y']), int(params['color'])
        # start background task
        sio.start_background_task(task_set_board, x=x, y=y, color=clr)
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
        return json.dumps({'code': 'time', 'status': str(next_time)})
    # execption handeling
    except Exception as e:
        print(e, e.args)
        return 'undefined'


"""
    Preference Namespace
"""