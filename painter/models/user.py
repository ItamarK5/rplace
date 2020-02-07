from ..extensions import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float
from datetime import datetime
from sqlalchemy.orm import relationship, backref
from ..config import Config
from hashlib import pbkdf2_hmac


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    username = Column(String(15), unique=True, nullable=False)
    password = Column(String(64), nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    next_time = Column(Float(), default=0.0, nullable=False)
    pixels = relationship('Pixel', backref='users', lazy=True)
    sqlite_autoincrement = True

    def __init__(self, password=None, hash_password=None, **kwargs):
        if hash_password is not None and password is None:
            password = self.encrypt_password(hash_password)
        super().__init__(password=password, **kwargs)

    @staticmethod
    def encrypt_password(password: str) -> bytes:
        return pbkdf2_hmac(
            'sha512',
            password.encode(),
            Config.USER_PASSWORD_SALT,
            Config.USER_PASSWORD_ROUNDS
        )

    def __repr__(self):
        return f"<User(name={self.name}>"

    def get_next_time(self):
        return datetime.fromtimestamp(self.next_time)

    def set_next_time(self, next_time: datetime):
        self.next_time = next_time.timestamp()
