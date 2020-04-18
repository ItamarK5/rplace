"""
 A backend to work with the board on redis
"""
from threading import Lock

from .extensions import redis, cache


# the key for the board in redis database
_BOARD_REDIS_KEY = 'board'

BOARD_BYTES_SIZE = 1000*500


def make_board() -> bool:
    """
    :return: if there is a board
    check if there is a board object in redis
    if not creates new one
    """
    if not redis.exists(_BOARD_REDIS_KEY):
        return bool(redis.set(_BOARD_REDIS_KEY, '\00' * BOARD_BYTES_SIZE))
    return True


def set_at(x: int, y: int, color: int) -> None:
    """
    :param x: x of the colored pixel
    :param y: y of the colored pixel
    :param color: the color the user setted the pixel
    :return: nothing
    set a pixel on the board copy in the redis server
    """
    bitfield = redis.bitfield(_BOARD_REDIS_KEY)
    # need to count for little endian
    x_endian = x + (-1)**(x % 2)
    bitfield.set('u4', (y * 1000 + x_endian) * 4, color)
    bitfield.execute()


@cache.cached(timeout=1)
def get_board() -> bytes:
    """
    :return: returns a copy of the board in bytes format
    """
    return redis.get(_BOARD_REDIS_KEY)


def drop_board() -> bool:
    """
    deletes the board
    :return: if board was deleated
    :rtype: bool
    """
    if not redis.exists(_BOARD_REDIS_KEY):
        return False
    return bool(redis.delete(_BOARD_REDIS_KEY))


__all__ = [
    'make_board',
    'set_at',
    'drop_board',
    'get_board',
]
