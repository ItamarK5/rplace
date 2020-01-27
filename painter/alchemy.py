import urllib
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from .functions import encrypt_password
import sqlalchemy
from datetime import datetime
from .consts import *

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(64), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    next_time = db.Column(db.Float(), default=0.0, nullable=False)
    is_active = db.Column(db.Boolean(), default=False, nullable=False)

    def __repr__(self):
        return f"<User(name={self.name}>"

    def set_password(self, password):
        self.password = encrypt_password(self.username, password)

    def get_next_time(self):
        return datetime.fromtimestamp(self.next_time)
        
    def set_next_time(self, next_time: datetime):
        self.next_time = next_time.timestamp()