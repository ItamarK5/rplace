import re
from os import path
from datetime import timedelta

MIME_TYPES = {
    'png': 'image/png',
    'ico': 'image/x-icon',
    'css': 'text/css',
    'js': 'text/javascript',
    'webp': 'image/webp',
    'jpg': 'image/jpg',
    'jfif': 'image/jpg',
    'gif': 'image/gif'
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
reNAME = re.compile(r'^[A-Z0-9]{5,16}$', re.I)
rePSWD = re.compile(r'^[A-F0-9]{64}$', re.I)  # password hashed so get hash value
