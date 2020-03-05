from typing import NoReturn
from threading import Lock
from flask import Flask
from .redis_backend import rds_backend

_set_lock = Lock()


def make_board() -> NoReturn:
    """
    :return: nothing
    check if there is a board object in redis
    if not creates new one
    """
    if not rds_backend.exists('board'):
        rds_backend.set('board', '\00' * 1000 * 500)


def init_app(app: Flask) -> NoReturn:
    """
    :param app: a flask appilcation
    :return: nothing
    runs functions on the app before starting the application
    -- creates the board
    """
    app.before_first_request(make_board)


def acquire_board_lock() -> NoReturn:
    """
    :return: nothing
    captures the set_lock of the board
    """
    _set_lock.acquire()


def release_board_lock():
    """
    :return: nothing
    releases the captures lock, works only if captured it before
    """
    _set_lock.release()


def set_at(x: int, y: int, color: int) -> NoReturn:
    """
    :param x:
    :param y:
    :param color:
    :return: nothing
    set a pixel on the board copy in the redis server
    """
    bitfield = rds_backend.bitfield('board')
    bitfield.set('u4', (y * 1000 + x) * 4, color)
    bitfield.execute()


def get_board() -> bytes:
    """
    :return: returns a copy of the board in bytes format
    """
    return rds_backend.get('board')


def debug_board() -> NoReturn:
    """
    :return: prints the board, for debug purpose
    """
    brd = get_board()
    for i in range(1000):
        print(brd[i * 500:(i + 1) * 500])


__all__ = [
    'make_board',
    'set_at',
    'init_app',
    'acquire_board_lock',
    'release_board_lock',
    'get_board',
    'debug_board'
]
