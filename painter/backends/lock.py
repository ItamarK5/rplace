"""
repsents working with lock object with the redis database
"""
from .extensions import redis

_DISABLE = 0  # False
_ENABLE = 1  # True
_ENABLE_EDIT_BOARD_KEY = 'enable-edit-board'
_flag_lock = False


def create_lock() -> bool:
    if not redis.exists(_ENABLE_EDIT_BOARD_KEY):
        return bool(redis.set(_ENABLE_EDIT_BOARD_KEY, _ENABLE))  # default allow
    return False


def drop_lock() -> bool:
    if redis.exists(_ENABLE_EDIT_BOARD_KEY):
        return bool(redis.delete(_ENABLE_EDIT_BOARD_KEY, _ENABLE))  # default allow
    return False


def is_enabled() -> bool:
    return redis.get(_ENABLE_EDIT_BOARD_KEY) == _ENABLE


def enable() -> bool:
    """
    enable setting pixel on board
    :return: if changed the redis value
    """
    return bool(redis.set(_ENABLE_EDIT_BOARD_KEY, _ENABLE))


def disable() -> bool:
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
        return enable()
    # else
    return disable()


__all__ = ['enable', 'disable', 'is_enabled', 'set_switch', 'create_lock']
