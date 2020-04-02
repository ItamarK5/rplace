from painter.others.constants import WEB_FOLDER
from os import path
from flask import Blueprint
# router blueprint -> routing all pages that relate to authorization
accounts_router = Blueprint('auth',
                            'auth',
                            template_folder=path.join(WEB_FOLDER, 'templates'))

from . import commands
from . import urls
from .utils import TokenSerializer

@accounts_router.before_app_first_request
def init_tokens() -> None:
    """
    :return: init the token generator object
    """
    TokenSerializer.init_serializer(current_app)
