import re
from datetime import datetime
from hashlib import pbkdf2_hmac
from typing import Optional, TypeVar

from flask import Markup
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, desc
from sqlalchemy.dialects.sqlite import DATETIME, SMALLINT

from painter.backends.extensions import datastore, cache
from painter.backends.extensions import login_manager
from .enumint import SmallEnum
from .notes import Record, Note
from .role import Role
from .. import app

reNAME = re.compile(r'^[A-Z0-9]{5,16}$', re.I)
rePSWD = re.compile(r'^[a-f0-9]{128}$')  # password hashed so get hash value


# only defiend for the current model to user
#_CachedRecordID, types for the options that the caching can cache

_CachedRecordID = TypeVar('_CachedRecordID', str, int)
_NO_RECORD = 'none'


class User(datastore.Model, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    username = Column(String(15), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    next_time = Column(DATETIME(), default=datetime.utcnow, nullable=False)
    # when the user created
    creation = Column(DATETIME(), default=datetime.utcnow, nullable=False)
    role = Column(SmallEnum(Role), default=Role.common, nullable=False)
    x = Column(SMALLINT(), default=500, nullable=False)
    # start y default
    y = Column(SMALLINT(), default=500, nullable=False)

    # default scale value, 4
    scale = Column(SMALLINT(), default=4, nullable=False)

    # default color when entering, black
    color = Column(SMALLINT(), default=1, nullable=False)

    # default url
    url = Column(String(), default=None, nullable=True)

    # https://stackoverflow.com/a/11579347
    sqlite_autoincrement = True

    def __init__(self, password=None, hash_password=None, **kwargs) -> None:
        """
        :param password: raw password
        :param hash_password: the password post hash
        :param kwargs: the other arguments passed to the Modal constructor
        to switch between initing using hashed password or not
        """
        if hash_password is not None and password is None:
            password = self.encrypt_password(kwargs.get('username'), hash_password)
        super().__init__(password=password, **kwargs)

    @property
    def related_notes(self):
        return Note.query.filter_by(user_subject_id=self.id).order_by(desc(Note.post_date))

    def set_password(self, password: str) -> None:
        """
        :param password: sets the user password
        :return: sets the users password
        """
        self.password = self.encrypt_password(password, self.username)

    @staticmethod
    def encrypt_password(password: str, username: str) -> str:
        return pbkdf2_hmac(
            'sha512',
            password.encode(),
            username.encode(),
            app.config['USER_PASSWORD_ROUNDS']
        ).hex()

    def __repr__(self) -> str:
        return f"<User(name={self.username}>"

    def has_required_status(self, role: Role) -> bool:
        """
        :param role: Enum represting the users current rule
        :return: if the user is the level of the rule or above
        """
        return self.role >= role    # role is IntEnum

    def is_superior_to(self, other: 'User') -> bool:
        """

        :param other: nothing
        :return: if the user superier to the other user
        """
        return self.role > other.role or self.role == Role.superuser

    def can_edit_note(self, note: Note) -> bool:
        return self.id == note.user_writer_id

    def get_id(self) -> str:
        """
        :return: the "id" of the user, the key to be used to identified it
        first 8 characters are
        """
        return super().get_id() + '&' + self.password

    @cache.memoize(timeout=300)
    def __get_last_record(self) -> Optional[str]:
        """
        :return: an in
        assumes that the notes are sorted by ids, that are auto
        """
        record = self.related_notes.first()
        if record is None:
            return 'none'
        return record.id

    def get_last_record(self) -> Optional[Record]:
        """
        :return: the last record written for the user, None if there arent any record
        it uses the method __get_last_record for caching the result to handle less requirements
        """
        identifier = self.__get_last_record()
        return None if identifier else Record.query.get(identifier)

    @property
    def is_active(self) -> bool:
        """
        :return: user if the user active -> can login
        """
        last_record = self.get_last_record()
        if last_record is None:  # user has not record
            return True
        if last_record.affect_from is None:  # record has no expire date
            return last_record.active
        if last_record.affect_from < datetime.now():
            datastore.session.add(Record(user=self,
                                         result=not last_record.active,
                                         declared=datetime.now(),
                                         reason='Timed passed',
                                         description=f"The record was set to expire at {last_record.affect_from}"
                                                     f"and the user tried to log in"
                                         ))
            self.forget_last_record()
            return not last_record.active  # replace the active
        # else
        return last_record.active  # isnt expired, so must has the other status

    def forget_last_record(self):
        cache.delete_memoized(self.__get_last_record, self)

    def record_message(self) -> Optional[Markup]:
        """
        :return: returns record message for a banned user, if the user isnt banned it returns None
        """
        record = self.get_last_record()
        if record is None:
            return None
        # else
        text = f'user {self.username}, you are banned from Social Painter, '
        if record.affect_from is not None:
            text += f"until {record.affect_from.strftime('%m/%d/%Y, %H:%M')}, "
        return Markup(text + f'because you <b>{record.reason}</b>')


@login_manager.user_loader
def load_user(user_token: str) -> Optional[User]:
    """
    :param user_token: the string value saved in a cookie/session of the user.
    :return: the matched user for the token
    token is in the form of: id&password
    flask encrypts it so I dont worry
    """
    print(user_token)
    # first get the id
    identity_keys = user_token.split('&')  # password hash, email, user_id
    # validate for user
    if len(identity_keys) != 2:
        return None
    # get user, determine if
    user_id, password = identity_keys
    if not user_id.isdigit():
        return None
    user = User.query.get(int(user_id))
    # check for the validation of the identifier and keys
    # also prevent user if he isnt active -> banned
    if (not user) or user.password != password:
        return None
    return user
