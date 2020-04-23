"""
 A backend to work with the board on redis
"""
from threading import Lock

from .extensions import redis, cache


# the key for the board in redis database
KEY = 'board'

BOARD_BYTES_SIZE = 1000*500


def make_board() -> bool:
    """
    :return: if there is a board
    check if there is a board object in redis
    if not creates new one
    """
    if not redis.exists(KEY):
        return bool(redis.set(KEY, '\00' * BOARD_BYTES_SIZE))
    return True


@cache.cached(timeout=1)
def get_board() -> str:
    """
    :return: the board from the database
    cached for 1 second because of timeout
    """
    return redis.get(KEY)


def set_at(x: int, y: int, color: int) -> None:
    """
    :param x: x of the colored pixel
    :param y: y of the colored pixel
    :param color: the color the user setted the pixel
    :return: nothing
    set a pixel on the board copy in the redis server
    """
    bitfield = redis.bitfield(KEY)
    # need to count for little endian
    x_endian = x + (-1)**(x % 2)
    bitfield.set('u4', (y * 1000 + x_endian) * 4, color)
    bitfield.execute()


def drop_board() -> bool:
    """
    deletes the board
    :return: if board was deleated
    :rtype: bool
    """
    if not redis.exists(KEY):
        return False
    return bool(redis.delete(KEY))


__all__ = [
    'make_board',
    'set_at',
    'drop_board',
    'get_board',
]
