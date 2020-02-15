from __future__ import annotations

from datetime import datetime
from os import path
from threading import Lock, Timer
from typing import Any, Dict, Optional, NoReturn

import numpy as np
from flask import Flask
from flask_login import current_user
from flask_socketio import SocketIO, emit, disconnect

from painter.constants import WEB_FOLDER
from painter.extensions import db
from .models.pixel import Pixel

BOARD_PATH = path.join(WEB_FOLDER, 'resources', 'board.npy')
COPY_BOARD_PATH = path.join(WEB_FOLDER, 'resources', 'board2.npy')

sio = SocketIO()


class Board:
    def __init__(self) -> None:
        self.board = self.open_board()
        #        self.__queue = Queue()
        self.__lock = Lock()

    @staticmethod
    def read_board(pth: str) -> Optional[np.ndarray]:
        brd = None
        if not path.exists(pth):
            return None
        try:
            brd = np.load(pth)
        finally:
            return brd

    @classmethod
    def open_board(cls) -> np.ndarray:
        """
            save board
        """
        brd = cls.read_board(BOARD_PATH)
        if brd is not None:
            return brd
        print('Board not loaded')
        brd = cls.read_board(COPY_BOARD_PATH)
        if brd is not None:
            return brd
        print('Board errored not loaded')
        # else
        # board = np.random.randint(0, 255, (1000, 500), np.uint8)
        return np.zeros((1000, 500), dtype=np.uint8)

    def init_app(self, app: Flask) -> NoReturn:
        app.before_first_request(self.save_board)

    #        app.before_first_request(self.process_board)

    def set_at(self, x, y, color) -> NoReturn:
        sio.start_background_task(self.__set_at, x=x, y=y, color=color)

    def __set_at(self, x, y, color) -> NoReturn:
        self.__lock.acquire()
        self.board[y, x // 2] &= 0x1111 << (x % 2) * 4
        self.board[y, x // 2] |= color << (1 - (x % 2)) * 4
        emit('set-board', (x, y, color), brodcast=True)
        self.__lock.release()

    def save_board(self) -> NoReturn:
        self.__lock.acquire()
        brd = self.board.copy()
        self.__lock.release()
        np.save(BOARD_PATH, brd)
        np.save(COPY_BOARD_PATH, brd)
        Timer(60, self.save_board)

    def get_bytes(self) -> bytes:
        return self.board.tobytes()


board = Board()


@sio.on('connect')
def connect_handler() -> None:
    if not current_user.is_authenticated:
        disconnect()
        return
    # else
    sio.emit('place-start', {
        'board': board.get_bytes(), 'time': str(current_user.next_time)
    })


@sio.on('set-board')
def set_board(params: Dict[str, Any]) -> str:
    """
    :param params: params given to the Dictionary
    :return: string represent the next time the user can update the canvas,
             or undefined if couldn't update the screen
    """
    try:
        current_time = datetime.utcnow()
        if current_user.next_time > current_time:
            return str(current_user.next_time())
        # validating parameter
        if 'x' not in params or (not isinstance(params['x'], int)) or not (0 <= params['x'] < 1000):
            return 'undefined'
        if 'y' not in params or (not isinstance(params['y'], int)) or not (0 <= params['y'] < 1000):
            return 'undefined'
        if 'color' not in params or (not isinstance(params['color'], int)) or not (0 <= params['color'] < 16):
            return 'undefined'
        next_time = current_time  # + MINUTES_COOLDOWN
        current_user.next_time = next_time
        x, y, clr = int(params['x']), int(params['y']), int(params['color'])
        db.session.add(Pixel(x=x, y=y, color=clr, drawer=current_user.id, drawn=current_time.timestamp()))
        # board.set_at(x, y, clr)
        db.session.commit()
        emit('set-board', (x, y, clr), brodcast=True)
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
        print(next_time)
        return str(next_time)
    except Exception as e:
        print(e)
        return 'undefined'
