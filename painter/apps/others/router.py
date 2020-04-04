from os import path

from flask import Blueprint

from painter.others.constants import WEB_FOLDER

other_router = Blueprint(
    'other',
    'other',
    static_folder=path.join(WEB_FOLDER),
)