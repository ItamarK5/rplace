from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import DATETIME, BOOLEAN
from ..extensions import datastore
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
    declared = Column(DATETIME(), nullable=False)
    writer = Column(Integer(), ForeignKey('user.id'), nullable=False)
    ban_record = Column(Integer(), ForeignKey('record.id'), nullable=True)
    sqlite_autoincrement = True


class Record(datastore.Model):
    id = Column(Integer(), primary_key=True, unique=True, autoincrement=True)
    active = Column(BOOLEAN(), nullable=False)
    expire = Column(DATETIME(), nullable=True, default=None)
    reason = Column(String(), nullable=False)
    sqlite_autoincrement = True

    def message(self, name: str) -> str:
        start = f'user {name}, you are banned from Social Painter, '
        if self.expire is not None:
            start += f"until {self.expire.strftime('%m/%d/%Y, %H:%M')} "
        return start + f', because you <b>{self.reason}</b>'
