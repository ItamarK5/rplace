from ..extensions import db
from flask_login import UserMixin
from datetime import datetime
from flask import current_app
import hashlib
<<<<<<< HEAD
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
<<<<<<< HEAD


class Role(db.Model, RoleMixin):
=======
=======


class IntEnum(db.TypeDecorator):
    # https://stackoverflow.com/a/41634765
    impl = db.Integer
>>>>>>> parent of 9614fde... 2.4.3

    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

<<<<<<< HEAD
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
>>>>>>> parent of cc4db7e... 2.4.2
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
<<<<<<< HEAD
    sqlite_autoincrement = True

    def __repr__(self):
        return f"<User(name={self.name}>"

    def set_password(self, password):
        self.password = self.encrypt_password(password)

    def get_next_time(self):
        return datetime.fromtimestamp(self.next_time)

    def set_next_time(self, next_time: datetime):
        self.next_time = next_time.timestamp()
=======
=======
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

<<<<<<< HEAD
>>>>>>> parent of 9614fde... 2.4.3
    sqlite_autoincrement = True

=======
>>>>>>> parent of 300245e... 2.4.2
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
>>>>>>> parent of cc4db7e... 2.4.2
