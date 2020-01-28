import numpy as np
from flask_login import current_user
from flask_socketio import SocketIO, send, emit, disconnect
from os import path
from datetime import datetime
from .alchemy import db
from .consts import WEB_FOLDER, MINUTES_COOLDOWN
import time
from typing import Any, Dict, Optional


BOARD_PATH = path.join(WEB_FOLDER, 'resources', 'board.npy')
COPY_BOARD_PATH = path.join(WEB_FOLDER, 'resources', 'board2.npy')


def read_board(pth: str) -> Optional[np.ndarray]:
    if not path.exists(pth):
        return None
    try:
        return np.load(pth)
    except Exception:
        return None

#    except Exception as e:
 #       print(e)
  #  finally:
   #     return None


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
        np.save(COPY_BOARD_PATH, board)
        time.sleep(2)
        np.save(BOARD_PATH, board)
