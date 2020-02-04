import numpy as np
from flask_login import current_user
from flask_socketio import SocketIO, emit, disconnect
from os import path
from datetime import datetime
from painter.extensions import db
from .models.pixel import Pixel
from painter.constants import WEB_FOLDER, MINUTES_COOLDOWN
from typing import Any, Dict, Optional
from .functions import run_async
import time


BOARD_PATH = path.join(WEB_FOLDER, 'resources', 'board.npy')
COPY_BOARD_PATH = path.join(WEB_FOLDER, 'resources', 'board2.npy')


def read_board(pth: str) -> Optional[np.ndarray]:
    brd = None
    if not path.exists(pth):
        return None
    try:
        brd = np.load(pth)
    finally:
        return brd


def open_board() -> np.ndarray:
    """
        save board
    """
    brd = read_board(BOARD_PATH)
    if brd is not None:
        return brd
    print('Board not loaded')
    brd = read_board(COPY_BOARD_PATH)
    if brd is not None:
        return brd
    print('Board errored not loaded')
    # else
    # board = np.random.randint(0, 255, (1000, 500), np.uint8)
    return np.zeros((1000, 500), dtype=np.uint8)


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
        'board': board.tobytes(), 'time': str(tm)
    })


@sio.on('set-board')
def set_board(params: Dict[str, Any]) -> Optional[str]:
    current_time = datetime.utcnow()
    if current_user.get_next_time() > current_time:
        return str(current_user.get_next_time())
    # validating parameter
    if 'x' not in params or (not isinstance(params['x'], int)) or not (0 <= params['x'] < 1000):
        return 'null'
    if 'y' not in params or (not isinstance(params['y'], int)) or not (0 <= params['y'] < 1000):
        return 'null'
    if 'color' not in params or (not isinstance(params['color'], int)) or not (0 <= params['color'] < 16):
        return 'null'
    next_time = current_time + MINUTES_COOLDOWN
    current_user.set_next_time(next_time)
    x, y, clr = params['x'], params['y'], params['color']
    db.session.add(Pixel(x=x, y=y, color=clr, drawer=current_user.id, drawn=current_time.timestamp()))
    db.session.commit()
    # setting the board
    if x % 2 == 0:
        board[y, x // 2] &= 0xF0
        board[y, x // 2] |= clr
    else:
        board[y, x // 2] &= 0x0F
        board[y, x // 2] |= clr << 4
    run_async(emit('set-board', params, broadcast=True))
    return str(next_time)


@run_async('save board')
def start_save_board():
    time.sleep(1)
    brd = board.copy()
    while True:
        np.save(COPY_BOARD_PATH, brd)
        del brd
        time.sleep(2)
        brd = board.copy()
        np.save(BOARD_PATH, brd)
