"""
represents working with lock object with the redis database
"""
from typing import Optional

from redis.exceptions import RedisError

from .extensions import redis_store

_DISABLE = b'0'  # False
_ENABLE = b'1'  # True
KEY = 'enable-edit-board'


def create() -> bool:
    """
    creates the lock in the redis database
    don't check for errors
    :return: if lock created
    """
    if not redis_store.exists(KEY):
        return bool(redis_store.set(KEY, _ENABLE))  # default allow
    return False


def drop() -> bool:
    """
    :return: if to drop lock
    :rtype drop lock
    """
    try:
        if redis_store.exists(KEY):
            return bool(redis_store.delete(KEY, _ENABLE))  # default allow
        return False
    except RedisError:
        return False


def is_open_val(val: bytes) -> bool:
    """
    :param val: a val represent redis representation of lock
    :return: if lock is open, enabled
    """
    return val == _ENABLE


def is_open() -> Optional[bool]:
    """
    :return: is lock open  | None if cant get the server
    """
    try:
        return is_open_val(redis_store.get(KEY))
    except RedisError:
        return None


def open_lock() -> bool:
    """
    enable setting pixel on board
    :return: if changed the redis value
    """
    return bool(redis_store.set(KEY, _ENABLE))


def close_lock() -> bool:
    """
    disable setting pixel on board
    :return: if changed the redis value
    """
    return bool(redis_store.set(KEY, _DISABLE))


def set_switch(set_active: bool) -> bool:
    """
    utility function to set lock via boolean value, enable changing pixels by true otherwise disable
    :param set_active: if to set_the lock active
    :type  set_active: bool
    :return: if changed any value
    """
    if set_active:
        return open_lock()
    # else
    return close_lock()


__all__ = ['open_lock', 'close_lock', 'is_open', 'set_switch', 'create', 'is_open_val']
