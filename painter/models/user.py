import re
from datetime import datetime
from enum import IntEnum, auto
from hashlib import pbkdf2_hmac
from typing import NoReturn, Any, Type

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, SmallInteger, TypeDecorator
from sqlalchemy.orm import relationship

from ..config import Config
from ..extensions import db, login_manager

reNAME = re.compile(r'^[A-Z0-9]{5,16}$', re.I)
rePSWD = re.compile(r'^[a-f0-9]{128}$')  # password hashed so get hash value
reEMAIL = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
    re.IGNORECASE)


class Role(IntEnum):
    # https://docs.python.org/3/library/enum.html
    banned = auto()
    common = auto()
    admin = auto()


class SmallEnum(TypeDecorator):
    """
    Enables passing in a Python enum and storing the enum's *value* in the db.
    The default would have stored the enum's *name* (ie the string).
    """
    impl = SmallInteger

    def __init__(self, enum_type: Type[IntEnum], *args, **kwargs) -> None:
        super(SmallEnum, self).__init__(*args, **kwargs)
        self._enum_type = enum_type

    def process_bind_param(self, value: Any, dialect) -> int:
        # https://www.michaelcho.me/article/using-python-enums-in-sqlalchemy-models
        if isinstance(value, int):
            return value
        elif isinstance(value, self._enum_type):
            return value.value
        # else
        raise ValueError()

    def process_result_value(self, value, dialect) -> IntEnum:
        try:
            return self._enum_type(value)
        except ValueError:
            raise ValueError('user privilage value isnt valid: %s' % value)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    username = Column(String(15), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    next_time = Column(Float(), default=0.0, nullable=False)
    pixels = relationship('Pixel', backref='users', lazy=True)
    role = Column(SmallEnum(Role), default=Role.common, nullable=False)
    sqlite_autoincrement = True

    def __init__(self, password=None, hash_password=None, **kwargs):
        if hash_password is not None and password is None:
            password = self.encrypt_password(hash_password)
        super().__init__(password=password, **kwargs)

    @staticmethod
    def encrypt_password(password: str) -> str:
        return pbkdf2_hmac(
            'sha512',
            password.encode(),
            Config.USER_PASSWORD_SALT,
            Config.USER_PASSWORD_ROUNDS
        ).hex()

    def __repr__(self) -> str:
        return f"<User(name={self.username}>"

    def get_next_time(self) -> datetime:
        return datetime.fromtimestamp(self.next_time)

    def set_next_time(self, next_time: datetime) -> NoReturn:
        self.next_time = next_time.timestamp()


@login_manager.user_loader
def load_user(user_id: str) -> int:
    return User.query.get(int(user_id))
