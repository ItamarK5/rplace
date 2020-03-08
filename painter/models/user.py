from __future__ import annotations
import re
from datetime import datetime
from hashlib import pbkdf2_hmac
from typing import Optional
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.sqlite import DATETIME, SMALLINT
from sqlalchemy.orm import relationship
from .role import Role
from .enumint import SmallEnum
from ..config import Config
from ..extensions import datastore, login_manager
from .ban_status import BanRecord
from datetime import datetime
reNAME = re.compile(r'^[A-Z0-9]{5,16}$', re.I)
rePSWD = re.compile(r'^[a-f0-9]{128}$')  # password hashed so get hash value
reEMAIL = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
    re.IGNORECASE)


class User(datastore.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    username = Column(String(15), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    creation = Column(DATETIME(), default=datetime.utcnow, nullable=False)
    next_time = Column(DATETIME(), default=datetime.utcnow, nullable=False)
    pixels = relationship('Pixel', backref='users', lazy=True)
    role = Column(SmallEnum(Role), default=Role.common, nullable=False)
    x = Column(SMALLINT(), default=500, nullable=False)
    y = Column(SMALLINT(), default=500, nullable=False)
    scale = Column(SMALLINT(), default=4, nullable=False)
    color = Column(SMALLINT(), default=4, nullable=False)
    url = Column(String(), default=None, nullable=True)
    sqlite_autoincrement = True

    def __init__(self, password=None, hash_password=None, **kwargs) -> None:
        if hash_password is not None and password is None:
            password = self.encrypt_password(kwargs.get('username'), hash_password)
        super().__init__(password=password, **kwargs)

    def set_password(self, password: str) -> None:
        self.password = self.encrypt_password(password)

    @staticmethod
    def encrypt_password(password: str, username: str) -> str:
        return pbkdf2_hmac(
            'sha512',
            password.encode(),
            username.encode(),
            Config.USER_PASSWORD_ROUNDS
        ).hex()

    def __repr__(self) -> str:
        return f"<User(name={self.username}>"

    def has_required_status(self,
                            role: Role) -> bool:
        return self.role >= role

    def is_superior_to(self, other: User) -> bool:
        return self.role > other.role

    def get_id(self) -> str:
        """
        :return: the "id" of the user, the key to be used to identified it
        first 8 characters are
        """
        return super().get_id() + '&' + self.password

    def is_active(self):
        record = BanRecord.query.filter_by(user=self.id).order_by('-id').first()
        if record is None:
            return True
        if record.expired < datetime.now():
            
        return record is not None and record.result == True

@login_manager.user_loader
def load_user(user_token: str) -> Optional[User]:
    """
    :param user_token: the string value saved in a cookie/session of the user.
    :return: the matched user for the token
    id&password
    flask encrypts it so I dont worry
    """
    # first get the id
    identity_keys = user_token.split('&')  # password hash, email, user_id
    # validate for user
    if len(identity_keys) != 2 or not identity_keys[0].isdigit():
        return None
    # get user, determine if
    user_id, password = identity_keys
    user = User.query.get(int(user_id))
    if (not user) or user.password != password:
        return None
    return user
