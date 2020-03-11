from .extensions import rds_backend
from flask import Flask
"""
    represnting an ability of the admin to prevent users from setting pixels
"""
_DISABLE = 0    # False
_ENABLE = 1     # True
_ENABLE_EDIT_BOARD_KEY = 'enable-edit-board'
_enable_edit_board = False                      # determine if can shutdown the server


def create_object():
    if not rds_backend.exists(_ENABLE_EDIT_BOARD_KEY):
        rds_backend.set(_ENABLE_EDIT_BOARD_KEY, _ENABLE)     # default allow


def init_app(app: Flask) -> None:
    app.before_first_request(create_object)


def is_enabled():
    return _enable_edit_board   # but in reallity bool(rds_backend.get(_ENABLE_EDIT_BOARD_KEY)


def enable():
    global _enable_edit_board
    if _enable_edit_board:
        _enable_edit_board = False
        rds_backend.set(_ENABLE)
    # rds_backend.set(0)


def disable():
    global _enable_edit_board
    if _enable_edit_board:
        _enable_edit_board = False
        rds_backend.set(_DISABLE)
    # rds_backend.set(1)


__all__ = ['init_app', 'enable', 'disable', 'is_enabled']
