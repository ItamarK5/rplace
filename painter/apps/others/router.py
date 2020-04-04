from os import path

from flask import Blueprint


other_router = Blueprint(
    'other',
    'other',
    static_folder='/web',
)