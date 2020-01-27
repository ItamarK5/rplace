import numpy as np
from flask_login import current_user
from flask_socketio import SocketIO, send, emit, disconnect
from os import path
from datetime import datetime
from .alchemy import db
from .consts import WEB_FOLDER, MINUTES_COOLDOWN
import time
from typing import Any, Dict


BOARD_PATH = path.join(WEB_FOLDER, 'resoucres', 'board.npy')


def open_board() -> np.ndarray:
    """
        save board
    """
    if path.exists(BOARD_PATH):
        place_board = np.load(BOARD_PATH)
        print(place_board.shape)
    else:
        place_board = np.zeros((1000, 500), dtype=np.uint8)
        # board = np.random.randint(0, 255, (1000, 500), np.uint8)
    return place_board


sio = SocketIO()
board = open_board()


@sio.on('connect')
def connect_handler() -> None:
    if not current_user.is_authenticated:
        disconnect()
        return
    # else
    tm = current_user.get_next_time()
    sio.emit('place-start', {
        'board': board.tobytes(), 'cooldown_target': str(tm)
    })


@sio.on('set-board')
def set_board(params: Dict[str, Any]) -> None:
    current_time = datetime.now()
    if current_user.get_next_time() > current_time:
        emit('update-timer', str(current_user.get_next_time()))
        return
    # validating parameter
    if 'x' not in params or (not isinstance(params['x'], int)) or not (0 <= params['x'] < 1000):
        return
    if 'y' not in params or (not isinstance(params['y'], int)) or not (0 <= params['y'] < 1000):
        return
    if 'color' not in params or (not isinstance(params['color'], int)) or not (0 <= params['color'] < 16):
        return
    x, y, clr = params['x'], params['y'], params['color']
    # setting the board
    if x % 2 == 0:
        board[y, x // 2] &= 0xF0
        board[y, x // 2] |= clr
    else:
        board[y, x // 2] &= 0x0F
        board[y, x // 2] |= clr << 4
    next_time = current_time+MINUTES_COOLDOWN
    current_user.set_next_time(next_time)
    db.session.commit()
    emit('update-timer', str(next_time), brodcast=False)
    emit('set-board', params, broadcast=True)


def save_board():
    while True:
        time.sleep(10)
        np.save(BOARD_PATH, board)