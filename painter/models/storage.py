"""
Name: storage
file contains simplify models that only used to hold 1-3 keys, they mostly used
to remember simple staff easily
"""
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy import String, Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from painter.backends.extensions import datastore
from flask_sqlalchemy import BaseQuery


class ExpiredTextMixin(object):
    """
     An base for classes that inherit the flask_sqlalchemy model class
     that classes is a simple table cache, stores values for a limited amount of time
     the function mostly uses string for the checks
    """
    # no need for id
    max_expires_seconds: int  # use default instead of configured
    identity_column_name: str  # name of the table
    identity_max_length: int  # max length of the string
    query: BaseQuery
    creation_date = Column(DATETIME(), default=datetime.utcnow)  # now

    # its a class method
    @declared_attr
    def identity_column(cls) -> Column:
        return Column(
            cls.identity_column_name,
            String(cls.identity_max_length),
            primary_key=True,
            nullable=False
        )

    @classmethod
    def get_identified(cls, identity_string: str) -> 'ExpiredTextMixin':
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
            datastore.session.delete(model)
            datastore.session.commit()
            return False
        return True

    @classmethod
    def create_new(cls, identity_string: str) -> None:
        """
        :param identity_string: value matched the identity string column
        :return: nothing
        creates the table and submit it to the database, fastly
        """
        datastore.session.add(cls(identity_column=identity_string))
        datastore.session.commit()

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
        forced_add = cls.get_identified(identity_string)
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

    @classmethod
    def force_forget(cls, identity_string: str) -> bool:
        """
        :return:
        """
        model = cls.get_identified(identity_string)
        if model is None:
            return False
        # otherwise
        datastore.session.delete(model)
        datastore.session.commit()

    def has_expired(self) -> bool:
        return (datetime.utcnow() - self.creation_date).seconds > self.max_expires_seconds


class SignupMailRecord(datastore.Model, ExpiredTextMixin):
    """
        Used to cache a name of a new user.
        to prevent other users from using it
    """
    __tablename__ = 'sign_up_mail_record'
    max_expires_seconds = 900
    identity_column_name = 'mail_address'
    identity_max_length = 254


class SignupUsernameRecord(datastore.Model, ExpiredTextMixin):
    """
        Used to cache a mail of a new user
        to prevent reuse of it and re-mailing over and over again
    """
    __tablename__ = 'sign_up_username_record'
    max_expires_seconds = 3600
    identity_column_name = 'username'
    identity_max_length = 15


class RevokeMailRecord(datastore.Model, ExpiredTextMixin):
    __tablename__ = 'revoke_mail_address_record'
    max_expires_seconds = 3600
    identity_column_name = 'address'
    identity_max_length = 254


__all__ = [
    'SignupMailRecord',
    'SignupUsernameRecord',
    'RevokeMailRecord'
]
