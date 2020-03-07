from datetime import timedelta
from os import path

MIME_TYPES = {
    'png': 'image/png',
    'ico': 'image/x-icon',
    'css': 'text/css',
    'js': 'text/javascript',
    'webp': 'image/webp',
    'jpg': 'image/jpg',
    'jfif': 'image/jpg',
    'gif': 'image/gif',
    'jpeg': 'image/jpeg'
}

WEB_FOLDER = path.join(
    path.dirname(
        path.dirname(
            path.abspath(__file__)
        )
    ),
    'web'
)
# time
MINUTES_COOLDOWN = timedelta(minutes=1)
COLORS = (
    "white", "red", "olive", "blue",
    "black", "pink", "yellow", "aqua",
    "gray", "brown", "green", "purple",
    "silver", "orange", "lime", "magenta",
)
