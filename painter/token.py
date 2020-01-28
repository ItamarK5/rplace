from itsdangerous import URLSafeTimedSerializer, BadData
from .config import Config
from typing import Optional
# https://realpython.com/handling-email-confirmation-in-flask/
from .config import Config


def generate_confirmation_token(email:str) -> str:
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps(email, salt=Config.SECURITY_PASSWORD_SALT)


def confirm_token(token) -> Optional[BadData]:
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt=Config.SECURITY_PASSWORD_SALT,
            max_age=Config.MAX_TIME_FOR_USER_TO_REGISTER
        )
    except BadData as e:
        return e
    return email
