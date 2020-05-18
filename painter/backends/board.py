"""
 A backend to work with the board on redis
"""
from redis.exceptions import RedisError

from .extensions import redis_store, cache

# the key for the board in redis database
REDIS_KEY = 'board'

BOARD_BYTES_SIZE = 1000 * 500


def create() -> bool:
    """
    :return: if there is a board
    check if there is a board object in redis
    if not creates new one
    """
    try:
        if not redis_store.exists(REDIS_KEY):
            return bool(redis_store.set(REDIS_KEY, '\00' * BOARD_BYTES_SIZE))
        return True
    except RedisError:
        return False


@cache.cached(timeout=1)
def get_board() -> str:
    """
    :return: the board from the database
    cached for 1 second because of timeout
    """
    return redis_store.get(REDIS_KEY)


def set_at(x: int, y: int, color: int) -> None:
    """
    :param x: x of the colored pixel
    :param y: y of the colored pixel
    :param color: id of palette
    :return: nothing
    set a pixel on the board copy in the redis server
    """
    bitfield = redis_store.bitfield(REDIS_KEY)
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
        if not redis_store.exists(REDIS_KEY):
            return False
        return bool(redis_store.delete(REDIS_KEY))
    except RedisError:
        return False


__all__ = [
    'create',
    'set_at',
    'drop',
    'get_board',
]
