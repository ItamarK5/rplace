"""
 A backend to work with the board on redis
"""
from redis.exceptions import RedisError

from .extensions import redis_store, cache
from redis.exceptions import ConnectionError as RedisConnectionError
from typing import Optional
# the key for the board in redis database
KEY = 'board'

BOARD_BYTES_SIZE = 1000 * 500


def create() -> bool:
    """
    :return: if there is a board
    check if there is a board object in redis
    if not creates new one
    """
    try:
        if not redis_store.exists(KEY):
            return bool(redis_store.set(KEY, '\00' * BOARD_BYTES_SIZE))
        return True
    except RedisError:
        return False


def get_board() -> Optional[str]:
    """
    :return: the board from the database
    """
    try:
        return redis_store.get(KEY)
    except RedisConnectionError:
        return None


def set_at(x: int, y: int, color: int) -> None:
    """
    :param x: x of the colored pixel
    :param y: y of the colored pixel
    :param color: id of palette
    :return: nothing
    set a pixel on the board copy in the redis server
    """
    bitfield = redis_store.bitfield(KEY)
    # need to count for little endian
    x_endian = x + (-1) ** (x % 2)
    bitfield.set('u4', (y * 1000 + x_endian) * 4, color)
    bitfield.execute()


def drop() -> bool:
    """
    deletes the board
    :return: if the board was deleted completely
    """
    try:
        if not redis_store.exists(KEY):
            return False
        return bool(redis_store.delete(KEY))
    except RedisError:
        return False


__all__ = [
    'create',
    'set_at',
    'drop',
    'get_board',
]
