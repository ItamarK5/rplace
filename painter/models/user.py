from enum import IntEnum as IntEnumAbstract, auto
from ..extensions import db
from flask_login import UserMixin
from datetime import datetime
from flask import current_app
import hashlib


class IntEnum(db.TypeDecorator):
    # https://stackoverflow.com/a/41634765
    impl = db.Integer

    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    @staticmethod
    def process_bind_param(value, dialect):
        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)


class User(db.Model, UserMixin):
    class Role(IntEnumAbstract):
        banned = auto()
        user = auto()
        admin = auto()

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    next_time = db.Column(db.Float(), default=0.0, nullable=False)
    role = db.Column(IntEnum(Role), default=Role.user, nullable=False)
    pixels = db.relationship('Pixel', backref='users', lazy=True)

    def __repr__(self):
        return f"<User(name={self.name}>"

    def set_password(self, password):
        self.password = self.encrypt_password(password)

    def get_next_time(self):
        return datetime.fromtimestamp(self.next_time)

    def set_next_time(self, next_time: datetime):
        self.next_time = next_time.timestamp()

    @staticmethod
    def encrypt_password(password: str) -> bytes:
        return hashlib.pbkdf2_hmac('sha512',
                                   current_app.config['SECURITY_PASSWORD_SALT'],
                                   password.encode(),
                                   10000)

    def has_rank(self, role):
        return self.role >= role