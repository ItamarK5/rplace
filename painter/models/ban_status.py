from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.sqlite import DATETIME, BOOLEAN
from ..extensions import datastore
from datetime import datetime


class BanRecord(datastore.Model):
    id = Column(Integer(), primary_key=True, unique=True, autoincrement=True)
    user = Column(Integer(), ForeignKey('user.id'), nullable=True)
    active = Column(BOOLEAN(), nullable=False)
    declared = Column(DATETIME(), nullable=False)
    expired = Column(DATETIME(), nullable=True, default=True)
    sqlite_autoincrement = True
