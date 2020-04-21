"""
repsents working with lock object with the redis database
"""
from .extensions import redis

_DISABLE = b'0'  # False
_ENABLE = b'1'  # True
KEY = 'enable-edit-board'


def create_lock() -> bool:
    """
    creates the lock in the redis database
    dont check for errors
    :return: if lock created
    """
    if not redis.exists(KEY):
        return bool(redis.set(KEY, _ENABLE))  # default allow
    return False


def drop_lock() -> bool:
    """
    :return: if to drop lock
    :rtype drop lock
    """
    if redis.exists(KEY):
        return bool(redis.delete(KEY, _ENABLE))  # default allow
    return False


def is_open_val(val: bytes) -> bool:
    """
    :param val: a val represent redis represention of lock
    :return: if lock is open, enabled
    """
    return val == _ENABLE


def is_open() -> bool:
    """
    :return: is lock open
    """
    return is_open_val(redis.get(KEY))


def open_lock() -> bool:
    """
    enable setting pixel on board
    :return: if changed the redis value
    """
    return bool(redis.set(KEY, _ENABLE))


def close_lock() -> bool:
    """
    disable setting pixel on board
    :return: if changed the redis value
    """
    return bool(redis.set(KEY, _DISABLE))


def set_switch(set_active: bool) -> bool:
    """
    utility function to set lock via boolean value, enable chaging pixels by true otherwise disable
    :param set_active: if to set_the lock active
    :type  set_active: bool
    :return: if changed any value
    """
    if set_active:
        return open_lock()
    # else
    return close_lock()


__all__ = ['open_lock', 'close_lock', 'is_open', 'set_switch', 'create_lock', 'is_open_val']
