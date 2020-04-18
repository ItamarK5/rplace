"""
place router
the router handeling urls related to users/main app
"""

from os import path

from flask import Blueprint

place_router = Blueprint(
    'place',
    'place',
    static_folder=path.join('/web', 'static'),
)
