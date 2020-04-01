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
# folder for all web related staff.
WEB_FOLDER = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'web')
# time between each draw for user
MINUTES_COOLDOWN = timedelta(minutes=1)

# Colors of pixels in order
COLORS = (
    "white", "black", "gray", "silver",
    "red", "pink", "brown", "orange",
    "olive", "yellow", "green", "lime",
    "blue", "aqua", "purple", "magenta"
)
