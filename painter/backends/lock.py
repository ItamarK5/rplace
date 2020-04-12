"""
repsents working with lock object with the redis database
"""
from .extensions import redis

_DISABLE = b'0'  # False
_ENABLE = b'1'  # True
_ENABLE_EDIT_BOARD_KEY = 'enable-edit-board'
_flag_lock = False


def create_lock() -> bool:
    """
    creates the lock in the redis database
    dont check for errors
    :return: if lock created
    """
    if not redis.exists(_ENABLE_EDIT_BOARD_KEY):
        return bool(redis.set(_ENABLE_EDIT_BOARD_KEY, _ENABLE))  # default allow
    return False


def drop_lock() -> bool:
    """
    :return: if to drop lock
    :rtype drop lock
    """
    if redis.exists(_ENABLE_EDIT_BOARD_KEY):
        return bool(redis.delete(_ENABLE_EDIT_BOARD_KEY, _ENABLE))  # default allow
    return False


def is_open() -> bool:
    """
    :return: is lock open
    """
    return redis.get(_ENABLE_EDIT_BOARD_KEY) == _ENABLE


def open_lock() -> bool:
    """
    enable setting pixel on board
    :return: if changed the redis value
    """
    return bool(redis.set(_ENABLE_EDIT_BOARD_KEY, _ENABLE))


def close_lock() -> bool:
    """
    disable setting pixel on board
    :return: if changed the redis value
    """
    return bool(redis.set(_ENABLE_EDIT_BOARD_KEY, _DISABLE))


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


__all__ = ['open_lock', 'close_lock', 'is_open', 'set_switch', 'create_lock']
