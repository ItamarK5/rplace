from datetime import datetime
from typing import Dict

from sqlalchemy import Column, ForeignKey, Integer, String, case
from sqlalchemy.dialects.sqlite import DATETIME, BOOLEAN
from sqlalchemy.orm import relationship

from ..backends.extensions import datastore

"""
    need to ask what is better:
    1) Note and subclass of Note named Record
    2) Note with variations
    3) other Notes
"""


class Note(datastore.Model):
    id = Column(Integer(), primary_key=True, unique=True, autoincrement=True)
    user_subject_id = Column(Integer(), ForeignKey('user.id'), nullable=False)
    description = Column(String(), nullable=False)
    post_date = Column(DATETIME(), default=datetime.now, nullable=False)
    user_writer_id = Column(Integer(), ForeignKey('user.id'), nullable=False)
    is_record = Column(BOOLEAN(), nullable=True)

    # helped: https://stackoverflow.com/a/32899385
    # relationships
    user_subject = relationship('User', foreign_keys=user_subject_id, uselist=False, backref="subject")
    user_writer = relationship('User', foreign_keys=user_writer_id, uselist=False, backref='writer')

    sqlite_autoincrement = True
    __mapper_args__ = {
        'polymorphic_identity': 'note',
        'polymorphic_on': case(
            # sorry for pep 8, this is how it was in the example
            [(is_record == True, 'record'), ],
            else_='note'
        )
    }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('is_record', False)
        super().__init__(*args, **kwargs)

    def _json_format(self, user) -> Dict:
        return {
            'id': self.id,
            # 'writer': User.query.get(self.writer),
            'description': self.description,
            'post_date': self.post_date.strftime("%m/%d/%Y, %H:%M:%S"),
            'writer': self.user_writer.username,
            'type': 'note',
            'can_edit': user.can_edit_note(self)
        }

    def json_format(self, user):
        return self._json_format(user)


class Record(Note):
    id = Column(Integer(), ForeignKey('note.id'), primary_key=True)
    active = Column(BOOLEAN(), nullable=False)
    affect_from = Column(DATETIME(), nullable=True, default=None)
    reason = Column(String(), nullable=False)
    sqlite_autoincrement = True
    __mapper_args__ = {
        'polymorphic_identity': 'record'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(is_record=True, *args, **kwargs)

    def __get_note_type(self):
        if self.active and self.affect_from:
            return 'unbanned_date'
        elif self.active and not self.affect_from:
            return 'unbanned'
        elif (not self.active) and not self.affect_from:
            return 'banned'
        elif self.affect_from and not self.active:
            return 'banned_date'

    def _json_format(self, user) -> Dict:
        # get type
        dictionary = super()._json_format(user)
        dictionary.update({
            'type': self.__get_note_type(),
            'affect_from': self.affect_from if self.affect_from is not None else None,
            'reason': str(self.reason),
            'active': self.active
        })
        return dictionary
