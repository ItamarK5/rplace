from datetime import datetime
from typing import Dict, Any

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.sqlite import DATETIME, BOOLEAN
from sqlalchemy.orm import relationship

from ..backends.extensions import storage_sql

"""
    need to ask what is better:
    1) Note and subclass of Note named Record
    2) Note with variations
    3) other Notes
"""


class Note(storage_sql.Model):
    """
    Note modal
    SQLAlchemy of notes, notes that are written about users to remember
    later.
    """
    # polymorphic identity
    polymorphic_identity = Column(String(), nullable=False)

    # note identifier
    id = Column(Integer(), primary_key=True, unique=True, autoincrement=True)

    # the user the note was written about
    user_subject_id = Column(Integer(), ForeignKey('user.id'), nullable=False)

    # description about the user
    description = Column(String(), nullable=False)

    # the date the note was posted
    post_date = Column(DATETIME(), default=datetime.now, nullable=False)

    # the id of the user who writed the note
    user_writer_id = Column(Integer(), ForeignKey('user.id'), nullable=False)

    # if the note is a record (see down)
    is_record = Column(BOOLEAN(), nullable=True)

    # relationships
    user_subject = relationship('User', back_populates='notes')
    user_writer = relationship('User', back_populates='writer')

    # autoincrement of sqlite
    sqlite_autoincrement = True

    """
        maps for record
        record are all notes with record data related
    """
    __mapper_args__ = {
        'polymorphic_identity': 'note',
        # whats decided if record or note
        'polymorphic_with': '[Note, Record]',
        'polymorphic_on': polymorphic_identity
    }

    def __init__(self, *args, **kwargs):
        """
        :param args: init args
        :param kwargs: init kwargs
        wrapper for datastore.Model,
        set that the value of is_record is False if isnt already set (by Record constrctor)
        """
        kwargs.setdefault('is_record', False)
        super().__init__(*args, **kwargs)

    def equals(self, other: 'Note'):
        """
        :param other: it would be danger to mess with __eq__ because it is used by the sqlite model,
        so I em using equals method
        # source: https://stackoverflow.com/q/3453180
        :return: True if object specific identifiers are equal, the date and id
        """
        return other.id == self.id and other.post_date == self.post_date

    def _json_format(self, user) -> Dict[str, Any]:
        """
        :param user: user
        :return: the json data of the notes, the value of can_edit is determine by the passd user
        """
        return {
            'id': self.id,
            # 'writer': User.query.get(self.writer),
            'description': self.description,
            'post_date': self.post_date.strftime("%m/%d/%Y, %H:%M:%S"),
            'writer': self.user_writer.username,
            'type': 'note',
            'can_edit': user.can_edit_note(self)
        }

    def json_format(self, user) -> Dict[str, Any]:
        """
        :param user:
        :return: the json dictionary of the Note
        """
        return self._json_format(user)


class Record(Note):
    """
    A class hat inherits from record that represent a record about the user
    a record can change the active state if the user to prevent him from login or allow him
    """
    # identifier of the record -> to match for the note the contains the note related staff of the record
    id = Column(Integer(), ForeignKey('note.id'), primary_key=True)
    # if the user is setted to not active in the records
    active = Column(BOOLEAN(), nullable=False)
    # the date the record takes affect from, if null its the post date
    affect_from = Column(DATETIME(), nullable=True, default=None)
    # the reason for the record, displayed to the user when tries to log in
    reason = Column(String(), nullable=False)
    # auto increment
    sqlite_autoincrement = True
    # class inheritaces identity
    __mapper_args__ = {
        'polymorphic_identity': 'record'
    }

    def __init__(self, *args, **kwargs):
        """
        :param args: init args
        :param kwargs: kwargs args
        just adds a is_record to the init, so that it would be considered as record
        """
        super().__init__(is_record=True, *args, **kwargs)

    def __get_note_type(self):
        """
        :return: the type of note for specific json
        used in client side
        """
        if self.active and self.affect_from:
            return 'unbanned_date'
        elif self.active and not self.affect_from:
            return 'unbanned'
        elif (not self.active) and not self.affect_from:
            return 'banned'
        elif self.affect_from and not self.active:
            return 'banned_date'

    def _json_format(self, user) -> Dict:
        """
        :param user: user value
        :return: just wraps the original _json_format of Note, for record related saff
        """
        # get dictionary
        dictionary = super()._json_format(user)
        # update by values
        dictionary.update({
            'type': self.__get_note_type(),
            'affect_from': self.affect_from if self.affect_from is not None else None,
            'reason': str(self.reason),
            'active': self.active
        })
        return dictionary
