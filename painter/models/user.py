import re
from hashlib import pbkdf2_hmac
from typing import Optional
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, and_
from sqlalchemy.dialects.sqlite import DATETIME, SMALLINT
from sqlalchemy.orm import relationship
from .role import Role
from .enumint import SmallEnum
from ..config import Config
from ..extensions import datastore, cache
from painter.extensions import login_manager
from .notes import Record, Note
from datetime import datetime
from flask import Markup

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

    def is_superior_to(self, other) -> bool:
        return self.role > other.role or self.role == Role.superuser

    def get_id(self) -> str:
        """
        :return: the "id" of the user, the key to be used to identified it
        first 8 characters are
        """
        return super().get_id() + '&' + self.password

    @cache.memoize()
    def get_last_record(self) -> Optional[Note]:
        note = Note.query.filter(
            and_(
                Note.id == self.id,
                Note.ban_record is not None,
            )
        ).order_by(Note.declared.asc()).first()
        return note

    @property
    def is_active(self) -> bool:
        """
        :return: user if the user active -> can login
        """
        note = self.get_last_record()
        if note is None:      # user has not record
            return True
        record = Record.query.get(note.ban_record)
        if record.expire is None:   # record has no expire date
            print(record.active)
            return record.active
        if record.expire < datetime.now():
            datastore.session.add(Record(user=self,
                                         result=not record.active,
                                         declared=datetime.now(),
                                         reason='Timed passed',
                                         description=f"The record was set to expire at {record.expire}"
                                                     f"and the user tried to log in"
                                         ))
            self.forget_is_active()
            return not record.active       # replace the active
        # else
        return record.active       # isnt expired, so must has the other status

    def forget_is_active(self):
        cache.delete_memoized(self.get_last_record, self)

    def record_message(self) -> Optional[Markup]:
        note = self.get_last_record()
        if note is None:
            return
        # else
        record = Record.query.get(note.ban_record)
        text = f'user {self.username}, you are banned from Social Painter, '
        if record.expire is not None:
            text += f"until {record.expire.strftime('%m/%d/%Y, %H:%M')}, "
        return Markup(text + f'because you <b>{record.reason}</b>')


@login_manager.user_loader
def load_user(user_token: str) -> Optional[User]:
    """
    :param user_token: the string value saved in a cookie/session of the user.
    :return: the matched user for the token
    id&password
    flask encrypts it so I dont worry
    """
    print(user_token)
    # first get the id
    identity_keys = user_token.split('&')  # password hash, email, user_id
    # validate for user
    if len(identity_keys) != 2 or not identity_keys[0].isdigit():
        return None
    # get user, determine if
    user_id, password = identity_keys
    user = User.query.get(int(user_id))
    # check for the validation of the identifier and keys
    # also prevent user if he isnt active -> banned
    if (not user) or user.password != password:
        return None
    return user