from enum import IntEnum as IntEnumAbstract, auto
from ..extensions import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime
from flask import current_app
import hashlib
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, \
                       String, ForeignKey
from sqlalchemy.dialects.sqlite import DATETIME


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('users.id'))
    role_id = Column('role_id', Integer(), ForeignKey('roles.id'))


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(255))
    password = Column(String(255))
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    last_draw = Column(DATETIME())
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))
    pixels = db.relationship('Pixel', backref='users', lazy=True)

    sqlite_autoincrement = True

    def __repr__(self):
        return f"<User(name={self.name}>"

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