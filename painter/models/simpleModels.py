"""
Name: simpleModels
file contains simplify models that only used to hold 1-3 keys, they mostly used
to remember simple staff easily
"""
from flask import Flask
from abc import ABC, abstractproperty
from flask_sqlalchemy import Model
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy import String, Column, and_
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from painter.backends.extensions import datastore


class ExpiredTextBase(object):
    # no need for id
    max_expires_seconds: int    # use default instend of configured
    expires = Column(DATETIME(), default=datetime.utcnow)  #now
    identity_string = Column(String(), primary_key=True)    # ipv4

    @classmethod
    def check_string(cls, identity_string:str) -> bool:
        record = cls.identity_string.filter_by(remmeber_string=identity_string).first()
        # if expires
        if record is None:
            # create one
            datastore.sessoin.add(cls(identity_string=identity_string))
            return True
        if (datetime.utcnow()-record).seconds > cls.max_expires_seconds:
            try:
                datastore.session.delete(record)
            except NoResultFound:
                print('File has been found')
            return True
        return False

    @classmethod
    def force_add(cls, identity:str):
        forced_add = cls.identity_string.filter_by(identity=identity).first()
        if forced_add is None:
            return None
        else:
            forced_add.expires = datetime.utcnow()
            datastore.session.commit()
        return None


class RepeatRevokeMailRecord(Model, ExpiredTextBase):
    max_expires_seconds = 900


class SignupMailRecord(Model, ExpiredTextBase):
    max_expires_seconds = 900


class SignupUsernameRecord(Model, ExpiredTextBase):
    max_expires_seconds = 3600


class RegisterMailRecord(Model, ExpiredTextBase):
    max_expires_seconds = 3600


__all__ = [
    'RepeatRevokeMailRecord',
    'SignupMailRecord',
    'SignupUsernameRecord',
    'RegisterMailRecord'
]
