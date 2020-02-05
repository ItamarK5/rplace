from ..extensions import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref


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

    @staticmethod
    def process_bind_param(value, dialect):
        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)