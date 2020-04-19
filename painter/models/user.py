from datetime import datetime
from hashlib import pbkdf2_hmac
from typing import Optional, TypeVar, Union

from flask import Markup, current_app
from flask_login import UserMixin
from flask_sqlalchemy import BaseQuery
from sqlalchemy import Column, Integer, String, desc
from sqlalchemy.dialects.sqlite import DATETIME, SMALLINT

from painter.backends.extensions import datastore, cache
from painter.backends.extensions import login_manager
from .enumint import SmallEnum
from .notes import Record, Note
from .role import Role

"""
    only defiend for the current model to user
"""
_NO_RECORD = 'none'


class User(datastore.Model, UserMixin):
    """
    User model
    represent the data of a user of the app,
    inherits the UserMixin of flask_login so it will be supported by its methods
    inherits from the datastore.Model to have SQL values
    """
    __tablename__ = 'user'

    # id (identifier) integer the identify the object between others - for fast filtering uses integer
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    # the name of the user
    username = Column(String(15), unique=True, nullable=False)
    # password of the user -> saved as hash by the sha512 algorithem with the username as salt
    password = Column(String(128), nullable=False)
    # the user's email address, to send mails
    email = Column(String(254), unique=True, nullable=False)
    # the next time the user can draw on the bodr
    next_time = Column(DATETIME(), default=datetime.utcnow, nullable=False)
    # when the user was created
    creation_date = Column(DATETIME(), default=datetime.utcnow, nullable=False)
    # the role of the user
    role = Column(SmallEnum(Role), default=Role.common, nullable=False)
    # start x position
    x = Column(SMALLINT(), default=500, nullable=False)
    # start y position
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
    def related_notes(self) -> BaseQuery:
        """
        :return: all notes related to the user
        """
        return Note.query.filter_by(user_subject_id=self.id).order_by(desc(Note.post_date))

    def set_password(self, password: str) -> None:
        """
        :param password: sets the user password
        :return: sets the users password
        """
        self.password = self.encrypt_password(password, self.username)

    @staticmethod
    def encrypt_password(password: str, username: str) -> str:
        """
        :param password: encrypts the password
        :param username:
        :return: the encrypted password of the user
        must run only after app initilize
        """
        return pbkdf2_hmac(
            'sha512',
            password.encode(),
            username.encode(),
            current_app.config.get('APP_USER_PASSWORD_ROUNDS'),
        ).hex()

    def __repr__(self) -> str:
        """
        :return: string repression of the object with its primary key
        """
        return f"<User(name={self.username}>"

    def has_required_status(self, role: Role) -> bool:
        """
        :param role: Enum represting the users current rule
        :return: if the user is the level of the rule or above
        """
        return self.role >= role  # role is IntEnum

    def is_superior_to(self, other: 'User') -> bool:
        """

        :param other: nothing
        :return: if the user superior to the other user
        """
        return self.role > other.role or self.role == Role.superuser

    def can_edit_note(self, note: Note) -> bool:
        """
        :param note: a note object
        :return: if the user can edit the note, the user can edit the note if he is its writer
        or the user is superuser
        """
        if self.id == note.user_writer_id:
            return True
        # otherwise
        return self.has_required_status(Role.superuser)

    def get_id(self) -> str:
        """
        :return: the "id" of the user, the key to be used to identified it
        first 8 characters are
        """
        return super().get_id() + '&' + self.password

    @cache.memoize(timeout=300)
    def __get_last_record(self) -> Union[str, int]:
        """
        :return: id of the user
        assumes that the notes are sorted by ids, that are auto
        """
        record = self.related_notes.first()
        if record is None:
            return _NO_RECORD
        return record.id

    def get_last_record(self) -> Optional[Record]:
        """
        :return: the last record written for the user, None if there arent any record
        it uses the method __get_last_record for caching the result to handle less requirements
        """
        identifier = self.__get_last_record()
        return None if isinstance(identifier, str) else Record.query.get(identifier)

    @property
    def is_active(self) -> bool:
        """
        :return: user if the user active -> can login
        """
        last_record = self.get_last_record()
        if last_record is None:  # user has not record, he is free
            return True
        if last_record.affect_from is not None and last_record.affect_from < datetime.utcnow():
            # if started to take effect
            return not last_record.active  # replace the active
        # else
        return last_record.active  # isnt expired, so must has the other status

    def forget_last_record(self):
        """
        :return: nothing
        deletes the memory about the last record of the user
        """
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
    # also prevent user if he isn't active -> banned
    if (not user) or user.password != password or not user.is_active:
        return None
    return user

