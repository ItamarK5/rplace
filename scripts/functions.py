from typing import Optional
import hashlib

def encrypt_password(username:str, password:str):
    return hashlib.pbkdf2_hmac('sha512',username.encode(), password.encode(), 10000)

def get_file_type(file_path:str) -> Optional[str]:
    index_start = file_path.rfind('.', -5)   # no file extension above 6 from those I use
    if index_start == -1:
        return file_path[index_start:]
    return None