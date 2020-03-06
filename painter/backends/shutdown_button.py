from .redis_backend import rds_backend
from flask import Flask


enable_edit_board = False        # determine if can shutdown the server

def create_object():
    if not rds_backend.exists('enable-edit-board'):
        rds_backend.set('enable-edit-board', True)     # default allow

def init_app(app: Flask) -> None:
    app.before_first_request(create_object)

def disable_edit_board(self):
    return False

def enable_edit_board(self):
    return False

__all__ = ['init_app']