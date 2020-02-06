from ..extensions import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from flask_security import UserMixin, RoleMixin
from datetime import datetime
from flask import current_app
import hashlib
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, backref


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))


class Role(db.Model, RoleMixin):
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, unique=True)
    username = Column(String(15), unique=True, nullable=False)
    password = Column(String(64), nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    next_time = Column(Float(), default=0.0, nullable=False)
    pixels = relationship('Pixel', backref='users', lazy=True)
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))
    active = Column(Boolean(), default=True)
    sqlite_autoincrement = True

    def __repr__(self):
        return f"<User(name={self.name}>"

    def set_password(self, password):
        self.password = self.encrypt_password(password)

    def get_next_time(self):
        return datetime.fromtimestamp(self.next_time)

    def set_next_time(self, next_time: datetime):
        self.next_time = next_time.timestamp()
