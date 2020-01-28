from itsdangerous import URLSafeTimedSerializer, TimedJSONWebSignatureSerializer
from .config import Config
from typing import Optional
# https://realpython.com/handling-email-confirmation-in-flask/
from .config import Config
from typing import Tuple


def generate_confirmation_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps(email, salt=Config.SECURITY_PASSWORD_SALT)


def confirm_token(token: str) -> Tuple[str, float]:
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.loads(
            token,
            return_timestamp=True,
            salt=Config.SECURITY_PASSWORD_SALT,
    )
