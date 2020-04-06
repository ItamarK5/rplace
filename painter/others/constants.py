from datetime import timedelta
# mime types the application send
# for some strange reason
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
# time between each draw for user
MINUTES_COOLDOWN = timedelta(minutes=1)

# Colors of pixels in order
COLORS = (
    "white", "black", "gray", "silver",
    "red", "pink", "brown", "orange",
    "olive", "yellow", "green", "lime",
    "blue", "aqua", "purple", "magenta"
)
PAINTER_ENV_NAME = 'SOCIAL-PAINTER-CONFIG-PATH'
DEFAULT_PATH = 'painter/config.json'
CELERY_TITLE = 'celery'
DEFAULT_TITLE = 'DEFAULT'
CONFIG_FILE_PATH_KEY = '__CONFIG_PATH'

MANAGER_TYPES_PARSE = {
    'int': int,
    'integer': int,
    'number': int,
    'float': float,
    'real': float,
    'str': str,
    'string': str,
    'text': str,
    'bytes': bytes,
    'byt': bytes,
    'bool': bool,
    'cond': bool,   # shortcut for condition
}
