from flask_script import Shell
from ..models import (
    SignupNameRecord, SignupMailRecord, RevokePasswordMailRecord,
    Role, Record, User, Note
)
from ..backends import board, lock
from flask import current_app
from ..backends.extensions import storage_sql


def _make_context():
    """
    :return: the shell context, a dictionary
    :rtype: Dict[str, Any] {the typing package}
    """
    return {
        'app': current_app,
        'Role': Role,
        'lock': lock,
        'board': board,
        'Record': Record,
        'Note': Note,
        'User': User,
        'SignupNameRecord': SignupNameRecord,
        'SignupMailRecord': SignupMailRecord,
        'RevokeMailAttempt': RevokePasswordMailRecord,
        'storage_sql': storage_sql
    }


shell_command = Shell(make_context=_make_context)

__all__ = ['shell_command']
