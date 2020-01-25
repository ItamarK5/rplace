import urllib
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from .functions import encrypt_password
import sqlalchemy
from datetime import datetime


db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(15), unique=True)
    password = db.Column(db.LargeBinary(64))
    email = db.Column(db.String(254), unique=True)
    last_time = db.Column(db.Float(), default=0.0)


    def __repr__(self):
        return f"<User(name={self.name}>"

    def set_password(self, password):
        self.password = encrypt_password(self.username, password)
    
    def set_username(self, username):
        self.password = encrypt_password(username, self.password)
        self.username = username

    def get_time(self):
        return datetime.fromtimestamp(self.last_time)
        
    def set_time(self, tm: float):
        self.last_time = datetime(tm)