from click import types
from datetime import timedelta
from typing import Optional, FrozenSet

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

"""
    options flags for service flags
"""
PRINT_OPTION_FLAG = 'print'
DURATION_OPTION_FLAG = 'timeout'
"""
    flags strings to check if option is in
"""
# type : Dict[str, Set[str]]
FLAG_SERVICES_OPTIONS = {
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
        """
        :param flags: list of all flags related to check-service
        :return: if needs an option flag and it isn't the set returns false, otherwise True
        """
        return self.option_flag is None or self.option_flag in flags


# the formats
SERVICE_RESULTS_FORMAT = (
    ServiceResultsPrint('{:^12}', 'SERVICE', 'service_name'),
    ServiceResultsPrint('{:^12}', 'STATUS', 'result'),
    ServiceResultsPrint('{:^15}', 'TASK DURATION', 'duration', DURATION_OPTION_FLAG),
)

REDIS_DATABASE_OPERATIONS = types.Choice(
    ('drop', 'create', 'reset')
)