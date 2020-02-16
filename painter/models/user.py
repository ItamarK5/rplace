import re
from hashlib import pbkdf2_hmac
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.orm import relationship

from ..config import Config
from ..extensions import db, login_manager
from .role import Role, SmallEnum


reNAME = re.compile(r'^[A-Z0-9]{5,16}$', re.I)
rePSWD = re.compile(r'^[a-f0-9]{128}$')  # password hashed so get hash value
reEMAIL = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
    re.IGNORECASE)


class BanTable(db.Model):
    __tablename__ = 'banned'
    banned_id = Column(Integer, primary_key=True)
    banned_time = Column(DATETIME(), nullable=True)
    description = Column(String(256), nullable=True)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    username = Column(String(15), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    creation = Column(DATETIME(), default=datetime.utcnow, nullable=False)
    next_time = Column(DATETIME(), default=datetime.utcnow, nullable=False)
    pixels = relationship('Pixel', backref='users', lazy=True)
    role = Column(SmallEnum(Role), default=Role.common, nullable=False)
    sqlite_autoincrement = True

    def __init__(self, password=None, hash_password=None, **kwargs) -> None:
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


@login_manager.user_loader
def load_user(user_id: str) -> int:
    return User.query.get(int(user_id))