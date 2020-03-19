from threading import Lock

from flask import Flask

from .extensions import rds_backend

"""
A backend to work with the board on redis
"""

board_lock = Lock()
_BOADR_REDIS_KEY = 'board'
board_temp = b'\x00' * 500 * 1000


def make_board() -> None:
    """
    :return: nothing
    check if there is a board object in redis
    if not creates new one
    """
    if not rds_backend.exists('board'):
        rds_backend.set(_BOADR_REDIS_KEY, '\00' * 1000 * 500)


def init_app(app: Flask) -> None:
    """
    :param app: a flask appilcation
    :return: nothing
    runs functions on the app before starting the application
    -- creates the board
    """
    app.before_first_request(make_board)


def set_at(x: int, y: int, color: int) -> None:
    """
    :param x: x of the colored pixel
    :param y: y of the colored pixel
    :param color: the color the user setted the pixel
    :return: nothing
    set a pixel on the board copy in the redis server
    """
    """
    bitfield = rds_backend.bitfield(_BOADR_REDIS_KEY)
    # need to count for little endian
    x_endian = x + (-1)**(x % 2)
    bitfield.set('u4', (y * 1000 + x_endian) * 4, color)
    bitfield.execute()
    """
    pass


def get_board() -> bytes:
    """
    :return: returns a copy of the board in bytes format
    """
    # return rds_backend.get(_BOADR_REDIS_KEY)
    return board_temp


def debug_board() -> None:
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
    'board_lock',
    'get_board',
    'debug_board'
]
