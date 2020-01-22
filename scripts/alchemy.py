import urllib
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    ID = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return f"<User(name={self.name}>"

def init_app(app):
    db.init_app(app)
    return app