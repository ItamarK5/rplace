"""
Name: storage
file contains simplify models that only used to hold 1-3 keys, they mostly used
to remember simple staff easily
"""
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy import String, Column, and_
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from painter.backends.extensions import datastore


class ExpiredTextBase(object):
    """
     An base for classes that inherit the flask_sqlalchemy model class
     that classes is a simple table cache, stores values for a limited amount of time
     the function mostly uses string for the checks
    """
    # no need for id
    max_expires_seconds: int  # use default instead of configured
    identity_column_name: str  # name of the table
    identity_max_length: int  # max length of the string
    creation_date = Column(DATETIME(), default=datetime.utcnow)  # now

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
        """
        :param identity_string: value matched the identity string column
        :return: if there is matched row with the string in its identity string column
        """
        return cls.identity_column.filter_by(cls.identity_column
                                             ==
                                             identity_string).first() is None

    @classmethod
    def create_new(cls, identity_string: str) -> None:
        """
        :param identity_string: value matched the identity string column
        :return: nothing
        creates the table and submit it to the database, fastly
        """
        datastore.sessoin.add(**{cls.identity_column_name: identity_string})
        datastore.session.commit()

    @classmethod
    def check_string(cls, identity_string: str) -> bool:
        """
        :param identity_string: value matched the identity string column
        :return: if the value isn't "cached" in the database.
        first check if exists, by getting if there is any non unique object
        if exists, recreate it and add it.
        """
        record = cls.identity_column.filter_by(cls.identity_column == identity_string).first()
        # if expires
        if record is None:
            # create one
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
    def force_add(cls, identity_string: str):
        """
        :param identity_string: value matched the identity string column
        :return:
        """
        forced_add = cls.identity_column.filter_by(identity_string=identity_string).first()
        if forced_add is None:
            # create new one
            try:
                datastore.session.remove()
            # ignore already deleted result
            except NoResultFound:
                pass
        else:
            # reset the
            forced_add.expires = datetime.utcnow()
        datastore.session.commit()


class SignupMailRecord(datastore.Model, ExpiredTextBase):
    """
        Used to cache a name of a new user.
        to prevent other users from using it
    """
    __tablename__ = 'sign_up_mail_record'
    max_expires_seconds = 900
    identity_column_name = 'mail_address'
    identity_max_length = 254


class SignupUsernameRecord(datastore.Model, ExpiredTextBase):
    """
        Used to cache a mail of a new user
        to prevent reuse of it and re-mailing over and over again
    """
    __tablename__ = 'sign_up_username_record'
    max_expires_seconds = 3600
    identity_column_name = 'username'
    identity_max_length = 15


__all__ = [
    'SignupMailRecord',
    'SignupUsernameRecord',
]
