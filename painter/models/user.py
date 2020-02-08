from ..extensions import db, login_manager
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, Boolean
from datetime import datetime
from sqlalchemy.orm import relationship, backref
from ..config import Config
from hashlib import pbkdf2_hmac
from typing import NoReturn


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    username = Column(String(15), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    next_time = Column(Float(), default=0.0, nullable=False)
    pixels = relationship('Pixel', backref='users', lazy=True)
    is_admin = Column(Boolean(), default=False, nullable=False)
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
        return f"<User(name={self.name}>"

    def get_next_time(self) -> datetime:
        return datetime.fromtimestamp(self.next_time)

    def set_next_time(self, next_time: datetime) -> NoReturn:
        self.next_time = next_time.timestamp()


@login_manager.user_loader
def load_user(user_id: str) -> int:
    return User.query.get(int(user_id))
