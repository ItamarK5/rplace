from typing import Optional, FrozenSet
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
COLOR_COOLDOWN = timedelta(minutes=1)

# Colors of pixels in order
COLORS = (
    "white", "black", "gray", "silver",
    "red", "pink", "brown", "orange",
    "olive", "yellow", "green", "lime",
    "blue", "aqua", "purple", "magenta"
)
PAINTER_ENV_NAME = 'SOCIAL-PAINTER-CONFIG-PATH'
DEFAULT_PATH = 'painter/config.json'
CELERY_TITLE = 'Celery'
DEFAULT_TITLE = 'Default'
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
    'cond': bool,  # shortcut for condition
}


"""
    options flags for service flags
"""
PRINT_OPTION_FLAG = 'print'
DURATION_OPTION_FLAG = 'timeout'
"""
    flags strings to check if option is in
"""
# type : Dict[str, Set[str]]
FLAG_SERVICES_OPTINOS = {
    PRINT_OPTION_FLAG: {'p', 'print'},  # if to print debug staff
    DURATION_OPTION_FLAG: {'timeout', 't'},  # if display timeout
}

DEFAULT_MAX_AGE_USER_TOKEN = 3600


class ServiceResultsPrint:
    """
    object used to save options for check-service command
    """
    def __init__(self, string_format: str, title: str, key: str, option_flag: Optional[str] = None):
        """
        :param string_format: the format to enter the screen with string.format method
        :param title: title of the format
        :param key: key, key in dictionary of the response passed
        :param option_flag: specific string for flag_service_option,
        result with that parameter are only enabled if the option flag was passed
        to the check-sevice command
        """
        self.string_format = string_format
        self.title = title
        self.key = key
        self.option_flag = option_flag

    def is_option_enabled(self, flags: FrozenSet[str]) -> bool:
        print(self.title, self.option_flag is None or self.option_flag in flags)
        return self.option_flag is None or self.option_flag in flags


# the formats
SERVICE_RESULTS_FORMAT = (
    ServiceResultsPrint('{:^12}', 'SERVICE', 'service_name'),
    ServiceResultsPrint('{:^12}', 'STATUS', 'result'),
    ServiceResultsPrint('{:^15}', 'TASK DURATION', 'duration', DURATION_OPTION_FLAG),
)
