from ..extensions import db
from flask_login import UserMixin
from datetime import datetime
from flask import current_app
import hashlib


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    next_time = db.Column(db.Float(), default=0.0, nullable=False)
    is_active = db.Column(db.Boolean(), default=True, nullable=False)

    def __repr__(self):
        return f"<User(name={self.name}>"

    def set_password(self, password):
        self.password = self.encrypt_password(password)

    def get_next_time(self):
        return datetime.fromtimestamp(self.next_time)

    def set_next_time(self, next_time: datetime):
        self.next_time = next_time.timestamp()

    @staticmethod
    def encrypt_password(password: str) -> str:
        return hashlib.pbkdf2_hmac('sha512',
                                   current_app.config['SECURITY_PASSWORD_SALT'],
                                   password.encode(),
                                   10000).hex()