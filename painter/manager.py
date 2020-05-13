"""
    Author: Itamar Kanne
    the manager module decorates the app by command line parameter
    the module is based of flask_script module
    https://flask-script.readthedocs.io/en/latest/
"""
from __future__ import absolute_import

import subprocess
import sys
from typing import Iterable

from flask_script import Manager, Server, Option, Command
from flask_script.cli import prompt_bool, prompt_choices, prompt
from flask_script.commands import InvalidCommand

# first import app to prevent some time related import bugs
from .app import create_app, storage_sql, sio
from .manage import redis_manager, check_services_command, shell_command
from .models import Role, User, ExpireModels
from .others.constants import ROLE_OPTIONS
from .others.utils import (
    NewUserForm, MyCommand
)

manager = Manager(
    create_app,
    description='Social Painter CMD Service',
    help='Social Painter CMD Service\n'
         'if you want to start the server, follow the following steps:\n'
         'second use check-services --a to check if all services are available (services means outside support)'
         'third use start-redis --a to create all redis support',
    disable_argcomplete=False,
    with_default_commands=False
)

# configuration file
manager.add_option('--ic', '-import-class', dest='import_class',
                   help="which class to use for app",
                   required=False, default=None)
manager.add_option('--d', '-debug', dest='import_class',
                   help="which class to use for app",
                   required=False, default=None)

# init from other files
manager.add_command('redis', redis_manager)
manager.add_command('check-services', check_services_command)
manager.add_command('shell', shell_command)

class RunServer(Server):
    """
    Starts a production server
    """

    def get_options(self) -> Iterable[Option]:
        """
        options of the run-server command
        :return: option list
        """
        return (
            Option('-h', '--host', dest='host', help='host url of the server', default=None),
            Option('-p', '--port', dest='port', type=int, help='host port of the server', default=None),
            Option('-d', '--debug', action='store_true', dest='use_debugger', default=self.use_debugger,
                   help='enable the Werkzeug debugger (DO NOT use in production code)',
                   ),
            Option('-D', '--no-debug', action='store_false', dest='use_debugger', default=self.use_debugger,
                   help='disable the Werkzeug debugger'),
            Option('-r', '--reload', action='store_true', dest='use_reloader', default=self.use_reloader,
                   help='monitor Python files for changes (not 100%% safe for production use)',
                   ),
            Option('-R', '--no-reload', action='store_false', dest='use_reloader', default=self.use_reloader,
                   help='do not monitor Python files for changes')
        )

    def __call__(self, app, host, port, use_debugger, use_reloader):
        """
        :param  host: host the ip to run the server
        :type:  host: int
        :param  port: port to listen on the ip
        :type   port: int
        :param  use_debugger: if to use debbugger while running the application
        :type   use_debugger: bool
        :param  use_reloader: if to use the reloader option of flask
        :type   use_reloader: bool
        :return: nothing
        override the default runserver command to start a Socket.IO server
        """
        host = host if host is not None else app.config.get('APP_HOST', '127.0.0.1')
        port = port if port is not None else app.config.get('APP_PORT', 8080)
        # if didn't given debugger
        if use_debugger is None:
            # use app.debug
            use_debugger = app.debug
            if use_debugger is None:
                use_debugger = True
        if use_reloader is None:
            use_reloader = app.debug or not app.config.get('WERKZEUG_RUN_MAIN', True)
        # runs the socketio server
        sio.run(
            app,
            host=host,
            port=port,
            debug=use_debugger,
            use_reloader=use_reloader,
            **self.server_options
        )


""" Create User """

def create_user(username, password, mail_address, role):
    """
    :param  username: name of the new user
    :type   username: Optional[str]
    :param  password: the password of the new user
    :type   password: Optional[str]
    :param  mail_address: the mail address of the new user
    :type   mail_address: Optional[str]
    :param  role: string representing the role of the user default superuser
    :type   role: Optional[str]
    :return:runs the command
    :rtype: None
    """
    if username is None:
        username = prompt('enter a username address of the user\n[username]')
    if password is None:
        password = prompt('you forgeot entering a password, pless enter 1\n[Password]')
    if mail_address is None:
        mail_address = prompt('enter a mail address of the user\n[Mail]')
    if role is None:
        # select choices
        role = prompt_choices(
            'You must pick a role, if not default is superuser\n',
            ROLE_OPTIONS,
            'superuser'
        )
    # get matched role
    role_matched = Role.get_member_or_none(role)
    # if user given a role but isnt valid
    if role_matched is None:
        raise InvalidCommand('Pless enter a valid role, not: {0}'.format(role))
    # check valid role
    form, is_valid = NewUserForm.fast_validation(
        username=username,
        password=password,
        mail_address=mail_address
    )
    if not is_valid:
        # to get first error
        for field in iter(form):
            for error in field.errors:
                raise InvalidCommand('{0}: {1}'.format(field.name, error))
    # create user
    else:
        user = User(
            username=username,
            decrypted_password=password,
            email=mail_address,
            role=role_matched
        )
        # save user
        storage_sql.session.add(user)
        storage_sql.session.commit()
        print('user created successfully')


create_user_command = MyCommand(
    create_user,
    description='create a new user in the system',
    help_text='creates a new user'
)

create_user_command.add_option(Option('--n', '-name', '-username', dest='username',
                                      help='username of the new user'))

create_user_command.add_option(Option('--p', '-password', '-pswd', dest='password',
                                      help='password of the new user'))

create_user_command.add_option(Option('--m', '-mail', '-addr', dest='mail_address',
                                      help='mail address of the new user'))

create_user_command.add_option(Option('--r', '-role', dest='role',
                                      choices=tuple(set(map(lambda i: i[1], ROLE_OPTIONS))),
                                      help="the user\'s role would be admin"))


manager.add_command('create-user', create_user_command)


class CeleryWorker(MyCommand):
    """Starts the celery worker."""
    capture_all_args = True
    help = 'Start an celery worker\n' \
           'if you want to name it (all workers must have different name) you need ' \
           'to enter --n (name)'

    def run(self, argv):
        """
        :param argv: string arguments
        :type argv: List[str]
        :return: None
        runs a celery worker
        """
        ret = subprocess.call(
            ['venv/scripts/celery.exe', 'worker',
             '-A', 'painter.tasks.worker.celery', '-P', 'eventlet'] + argv
        )
        sys.exit(ret)


# adding command
manager.add_command('celery', CeleryWorker)
manager.add_command("runserver", RunServer())

"""Create Database Command"""


def create_db(drop_first=False):
    """
    :param drop_first: if to fist drop all databases before creating
    :type drop_first: boolean
    :return: if to drop first
    """
    if drop_first and prompt_bool('Are you sure you want to drop the table'):
        storage_sql.drop_all()
        print('database dropped')
    storage_sql.create_all()
    print('database created successfully')


create_db_command = MyCommand(
    create_db,
    'creates the database',
)
# option to drop first before creating the database
create_db_command.add_option(
    Option('--d', '-drop', dest='drop_first',
           action='store_true', default=False,
           help='Drops the current database before creation')
)
manager.add_command('create-db', create_db_command)


# drop database
def drop_db():
    if prompt_bool('Are you sure to drop the database'):
        storage_sql.drop_all()
        print('You should re-create the database, see the create-db command')


drop_database_command = MyCommand(drop_db, 'drops the database entirely')
manager.add_command('drop-db', drop_database_command)

"""
 Check Service Command
 Command to check if services required for the app are working
"""


def clear_cache():
    """
        clears all unused cache of storage models
    """
    for model_class in ExpireModels:
        model_class.clear_cache(False)
    storage_sql.session.commit()
    print('Clear Cache Complete')


# adds clear cache command
manager.add_command('clear-cache', Command(clear_cache))
@manager.command
def graph():
    from sqlalchemy_schemadisplay import create_schema_graph

    # create the pydot graph object by autoloading all tables via a bound metadata object
    graph = create_schema_graph(metadata=storage_sql.metadata,
                                show_datatypes=True,  # The image would get nasty big if we'd show the datatypes
                                show_indexes=False,  # ditto for indexes
                                rankdir='LR',  # From left to right (instead of top to bottom)
                                concentrate=False  # Don't try to join the relation lines together
                                )
    graph.write_png('dbschema.png')  # write out the file
