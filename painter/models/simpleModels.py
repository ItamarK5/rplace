"""
Name: simpledatastore.Models
file contains simplify models that only used to hold 1-3 keys, they mostly used
to remember simple staff easily
"""
from painter.backends.extensions import datastore
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy import String, Column, and_
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from painter.backends.extensions import datastore


class ExpiredTextBase(object):
    # no need for id
    max_expires_seconds: int  # use default instend of configured
    identity_column_name: str  # name of the table
    identity_max_length: int  # max length of the string
    expires = Column(DATETIME(), default=datetime.utcnow)  # now

    # its a class method
    @declared_attr
    def identity_column(cls) -> Column:
        return Column(
            cls.identity_column_name,
            String(cls.identity_max_length),
            primary_key=True,
        )

    @classmethod
    def exists(cls, identity_string: str) -> bool:
        return cls.identity_column.filter_by(cls.identity_column
                                             ==
                                             identity_string).first() is None

    @classmethod
    def check_string(cls, identity_string: str) -> bool:
        record = cls.identity_column.filter_by(cls.identity_column
                                               ==
                                               identity_string).first()
        # if expires
        if record is None:
            # create one
            datastore.sessoin.add(**{cls.identity_column_name: identity_string})
            return True
        if (datetime.utcnow() - record).seconds > cls.max_expires_seconds:
            # error handling
            try:
                datastore.session.delete(record)
            except NoResultFound:
                print('File has been found')
            return True
        return False

    @classmethod
    def force_add(cls, identity: str):
        forced_add = cls.identity_column.filter_by(identity=identity).first()
        if forced_add is None:
            return None
        else:
            forced_add.expires = datetime.utcnow()
            datastore.session.commit()
        return None


class RevokeMailRecord(datastore.Model, ExpiredTextBase):
    __tablename__ = 'revoke_mail_records'
    max_expires_seconds = 900
    identity_column_name = 'mail_address'
    identity_max_length = 254


class SignupMailRecord(datastore.Model, ExpiredTextBase):
    __tablename__ = 'sign_up_mail_record'
    max_expires_seconds = 900
    identity_column_name = 'mail_address'
    identity_max_length = 254


class SignupUsernameRecord(datastore.Model, ExpiredTextBase):
    __tablename__ = 'sign_up_username_record'
    max_expires_seconds = 3600
    identity_column_name = 'username'
    identity_max_length = 15


__all__ = [
    'RevokeMailRecord',
    'SignupMailRecord',
    'SignupUsernameRecord',
]
