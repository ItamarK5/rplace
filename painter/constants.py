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
