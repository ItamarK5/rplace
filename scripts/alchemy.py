import urllib
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from .functions import encrypt_password
db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    ID = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return f"<User(name={self.name}>"

    def set_password(self, password):
        self.password = encrypt_password(self.username, password)
    
    def set_username(self, username):
        self.password = encrypt_password(username, self.password)
        self.username = username
    
        
def init_app(app):
    db.init_app(app)
    return app