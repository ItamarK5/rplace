from sqlalchemy import Column, ForeignKey, Integer, String, case
from sqlalchemy.dialects.sqlite import DATETIME, BOOLEAN
from painter.backends.extensions import datastore
from datetime import datetime

"""
    need to ask what is better:
    1) Note and subclass of Note named Record
    2) Note with variations
    3) other Notes
"""


class Note(datastore.Model):
    id = Column(Integer(), primary_key=True, unique=True, autoincrement=True)
    user = Column(Integer(), ForeignKey('user.id'), nullable=False)
    description = Column(String(), nullable=False)
    declared = Column(DATETIME(), default=datetime.now, nullable=False)
    writer = Column(Integer(), ForeignKey('user.id'), nullable=False)
    is_record = Column(BOOLEAN(), nullable=True)
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


class Record(Note):
    id = Column(Integer(), ForeignKey('note.id'), primary_key=True)
    active = Column(BOOLEAN(), nullable=False)
    expire = Column(DATETIME(), nullable=True, default=None)
    reason = Column(String(), nullable=False)
    sqlite_autoincrement = True
    __mapper_args__ = {
        'polymorphic_identity': 'record'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(is_record=True, *args, **kwargs)
