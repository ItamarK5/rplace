from .extensions import rds_backend
from flask import Flask
"""
    represnting an ability of the admin to prevent users from setting pixels
"""
_DISABLE = 0    # False
_ENABLE = 1     # True
_ENABLE_EDIT_BOARD_KEY = 'enable-edit-board'
_enable_edit_board = _ENABLE                      # determine if can shutdown the server
_flag_lock = False


def create_object():
    if not rds_backend.exists(_ENABLE_EDIT_BOARD_KEY):
        rds_backend.set(_ENABLE_EDIT_BOARD_KEY, _ENABLE)     # default allow


def init_app(app: Flask) -> None:
    app.before_first_request(create_object)


def is_enabled() -> bool:
    return _enable_edit_board == _ENABLE   # but in reallity bool(rds_backend.get(_ENABLE_EDIT_BOARD_KEY)


def enable() -> int:
    global _enable_edit_board, _flag_lock
    if _enable_edit_board != _ENABLE:
        _enable_edit_board = _ENABLE
    # return rds_backend.set(_ENABLE_EDIT_BOARD, _ENABLE)
    return 1


def disable() -> int:
    global _enable_edit_board
    if _enable_edit_board != _DISABLE:
        _enable_edit_board = _DISABLE
    # return rds_backend.set(_ENABLE_EDIT_BOARD, _DISALBE)
    # rds_backend.set(1)
    return 0


__all__ = ['init_app', 'enable', 'disable', 'is_enabled']
