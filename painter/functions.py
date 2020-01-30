from flask import current_app
from typing import Optional, Dict, Any, Generic, Hashable
import hashlib
from wtforms.validators import Email, ValidationError


def get_file_type(file_path:str) -> Optional[str]:
    index_start = file_path.rfind('.', -4)   # no file extension above 4 from those I use
    if index_start != -1:
        return file_path[index_start+1:]
    return None
