from flask import Flask

from .extensions import redis

"""
    represnting an ability of the admin to prevent users from setting pixels
"""
_DISABLE = 0  # False
_ENABLE = 1  # True
_ENABLE_EDIT_BOARD_KEY = 'enable-edit-board'
_enable_edit_board = _ENABLE  # determine if can shutdown the server
_flag_lock = False


def create_var():
    if not redis.exists(_ENABLE_EDIT_BOARD_KEY):
        redis.set(_ENABLE_EDIT_BOARD_KEY, _ENABLE)  # default allow


def is_enabled() -> bool:
    return _enable_edit_board == _ENABLE  # but in reallity bool(rds_backend.get(_ENABLE_EDIT_BOARD_KEY)


def enable() -> bool:
    global _enable_edit_board, _flag_lock
    if _enable_edit_board != _ENABLE:
        _enable_edit_board = _ENABLE
    # return rds_backend.set(_ENABLE_EDIT_BOARD, _ENABLE)
    return True


def disable() -> bool:
    global _enable_edit_board
    if _enable_edit_board != _DISABLE:
        _enable_edit_board = _DISABLE
    # return bool(rds_backend.set(_ENABLE_EDIT_BOARD, _DISALBE))
    # rds_backend.set(1)
    return True


def set_switch(set_active: bool) -> bool:
    if set_active:
        return enable()
    # else
    return disable()


__all__ = ['init_app', 'enable', 'disable', 'is_enabled', 'set_switch']
