from os import path
from datetime import timedelta

MIMETYPES = {
    'png': 'image/png',
    'ico': 'image/x-icon',
    'css': 'text/css',
    'js': 'text/javascript',
    'webp': 'image/webp',
    'jpg': 'image/jpg',
    'jfif': 'image/jpg'
}
WEB_FOLDER = path.join(
    path.dirname(
        path.dirname(
            path.abspath(__file__)
            )
        ),
    'web'
)

MINUTES_COOLDOWN = timedelta(minutes=1)