"""
 A backend to work with the board on redis
"""
from redis.exceptions import RedisError

from .extensions import redis, cache

# the key for the board in redis database
KEY = 'board'

BOARD_BYTES_SIZE = 1000*500


def create() -> bool:
    """
    :return: if there is a board
    check if there is a board object in redis
    if not creates new one
    """
    try:
        if not redis.exists(KEY):
            return bool(redis.set(KEY, '\00' * BOARD_BYTES_SIZE))
        return True
    except RedisError:
        return False


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
    :param color: id of palette
    :return: nothing
    set a pixel on the board copy in the redis server
    """
    bitfield = redis.bitfield(KEY)
    # need to count for little endian
    x_endian = x + (-1)**(x % 2)
    bitfield.set('u4', (y * 1000 + x_endian) * 4, color)
    bitfield.execute()


def drop() -> bool:
    """
    deletes the board
    :return: if the board was deleted completely
    """
    try:
        if not redis.exists(KEY):
            return False
        return bool(redis.delete(KEY))
    except RedisError:
        return False


__all__ = [
    'create',
    'set_at',
    'drop',
    'get_board',
]
