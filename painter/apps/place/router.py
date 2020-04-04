from os import path

from flask import Blueprint

from painter.others.constants import WEB_FOLDER

place_router = Blueprint(
    'place',
    'place',
    static_folder=path.join(WEB_FOLDER, 'static'),
)
