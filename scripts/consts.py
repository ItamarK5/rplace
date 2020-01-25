import os
from os import path
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
            os.path.abspath(__file__)
            )
        ),
    'web'
)
