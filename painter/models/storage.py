"""
Name: storage
file contains simplify models that only used to hold 1-3 keys, they mostly used
to remember simple staff easily
"""
import re
from datetime import datetime, timedelta
from typing import Optional
from flask import Flask
from flask_sqlalchemy import BaseQuery
from sqlalchemy import String, Column, DATETIME
from sqlalchemy.ext.declarative import declared_attr

from painter.backends.extensions import storage_sql
from painter.others.constants import DEFAULT_MAX_AGE_USER_TOKEN

# pattern for lowercase
catch_pattern = re.compile(r'((?:^[a-z]|[A-Z])(?:[a-z]+)?)')


def to_small_case(string: str) -> str:
    """
    :param string: string in format of upper case
    :return: translates it into
    """
    return '_'.join(word.lower() for word in catch_pattern.findall(string))


ExpireModels = []


# noinspection PyMethodParameters
class CacheTextBase(storage_sql.Model):
    """
     An base for classes that inherit the flask_sqlalchemy model class
     that classes is a simple table cache, stores values for a limited amount of time
     the function mostly uses string for the checks
    """
    __abstract__ = True
    # no need for id
    max_expires_seconds: int  # use default instead of configured
    identity_column_name: str  # name of the table
    identity_max_length: int  # max length of the string
    query: BaseQuery

    creation_date = Column(DATETIME(), default=datetime.utcnow)

    def __init_subclass__(cls, **kwargs) -> None:
        """
        :param kwargs: class arguments
        :return: none
        on init class
        """
        ExpireModels.append(cls)
        super().__init_subclass__()

    # its a class method

    @declared_attr
    def identity_column(cls) -> Column:
        """
        :return: column of the identity
        """
        return Column(
            cls.identity_column_name,
            String(cls.identity_max_length),
            primary_key=True,
            nullable=False
        )

    @declared_attr
    def __tablename__(cls) -> str:
        return to_small_case(cls.__name__)

    @classmethod
    def get_identified(cls, identity_string: str) -> Optional['CacheTextBase']:
        """
        :param identity_string: get the object matched to the identity string
        :return: the object or None
        :param identity_string: a string identifing the object
        :return: The matched cached object, if not None
        """
        return cls.query.filter(cls.identity_column == identity_string).first()

    @classmethod
    def exists(cls, identity_string: str) -> bool:
        """
        :param identity_string: value matched the identity string column
        :return: if there is matched row with the string in its identity string column
        """
        model = cls.get_identified(identity_string)
        if model is None:
            return False
        # else check if expires
        if model.has_expired():
            storage_sql.session.delete(model)
            storage_sql.session.commit()
            return False
        return True

    @classmethod
    def create_new(cls, identity_string: str, commit: bool = True) -> None:
        """
        :param identity_string: value matched the identity string column
        :param commit: if to commit session
        :return: nothing
        creates the table and submit it to the database, fast
        """
        storage_sql.session.add(cls(identity_column=identity_string))
        if commit:
            storage_sql.session.commit()

    @classmethod
    def check_string(cls, identity_string: str) -> bool:
        """
        :param identity_string: value matched the identity string column
        :return: if the value isn't "cached" in the database.
        first check if exists, by getting if there is any non unique object
        if exists, recreate it and add it.
        """
        record = cls.get_identified(identity_string)
        # if expires
        if record is None:
            # create one
            return True
        if record.has_expired():
            # error handling
            try:
                storage_sql.session.delete(record)
            finally:
                return True
        return False

    @classmethod
    def new_or_refresh(cls, identity_string: str) -> None:
        """
        :param identity_string: value matched the identity string column
        :return: None
        """
        forced_add = cls.get_identified(identity_string)
        if forced_add is None:
            # create new one
            cls.create_new(identity_string)
        else:
            # reset the
            forced_add.expires = datetime.utcnow()
            storage_sql.session.commit()

    @classmethod
    def force_forget(cls, identity_string: str) -> bool:
        """
        :return: if the object existed before it tried to forget
        forcing to forget the cached data
        """
        model = cls.get_identified(identity_string)
        if model is None:
            return False
        # otherwise
        storage_sql.session.delete(model)
        storage_sql.session.commit()
        return True

    def has_expired(self) -> bool:
        return (datetime.utcnow() - self.creation_date).seconds > self.max_expires_seconds

    @classmethod
    def clear_cache(cls, save_session: bool):
        cache_expires = datetime.utcnow() + timedelta(seconds=cls.max_expires_seconds)
        for row in cls.query.filter(cls.creation_date < cache_expires).all():
            storage_sql.session.delete(row)
        if save_session:
            storage_sql.session.commit()


class SignupMailRecord(CacheTextBase):
    """
        Used to cache a name of a new user.
        to prevent other users from using it
    """
    identity_column_name = 'mail_address'
    identity_max_length = 254


class SignupNameRecord(CacheTextBase):
    """
        Used to cache a mail of a new user
        to prevent reuse of it and re-mailing over and over again
    """
    identity_column_name = 'username'
    identity_max_length = 15


class RevokeMailAttempt(CacheTextBase):
    identity_column_name = 'address'
    identity_max_length = 254


def init_storage_models(app: Flask) -> None:
    """
    :param app: the flask application
    :return: none
    init the storage model
    """
    RevokeMailAttempt.max_expires_seconds = app.config.get('APP_MAX_AGE_USER_TOKEN', DEFAULT_MAX_AGE_USER_TOKEN)
    SignupNameRecord.max_expires_seconds = app.config.get('APP_MAX_AGE_USER_TOKEN', DEFAULT_MAX_AGE_USER_TOKEN)
    SignupMailRecord.max_expires_seconds = app.config.get('APP_MAX_AGE_USER_TOKEN', DEFAULT_MAX_AGE_USER_TOKEN)


__all__ = [
    'SignupMailRecord',
    'SignupNameRecord',
    'RevokeMailAttempt',
    'ExpireModels',
    'init_storage_models'
]
