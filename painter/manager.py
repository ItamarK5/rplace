"""
    Author: Itamar Kanne
    the manager module decorates the app by command line parameter
    the module is based of flask_script module
    https://flask-script.readthedocs.io/en/latest/
"""

import subprocess
import sys
import time
from typing import Iterable, Any, Dict, FrozenSet, Optional

import click
import flask.cli
from flask_script import Manager, Server, Option, Command
from flask_script.cli import prompt_bool, prompt_choices, prompt
from flask_script.commands import InvalidCommand
from redis import exceptions as redis_exception

# first import app to prevent some time related import bugs
from .app import datastore, sio, redis, create_app
from .backends import board, lock
from .models import Role, User, ExpireModels
from .others.constants import DURATION_OPTION_FLAG, PRINT_OPTION_FLAG, SERVICE_RESULTS_FORMAT
from .others.utils import (
    NewUserForm, MyCommand, parse_service_options, check_service_flag
)


@click.group(cls=flask.cli.FlaskGroup, create_app=create_app)
@click.option('-debug', '--D', is_flag=True, flag_value=True, help="debug the app in debug mode")
@flask.cli.with_appcontext
def cli(*args, **kwargs):
    print('Social Painter CMD Service')


manager = Manager(
    description='Social Painter CMD Service',
    help='Social Painter CMD Service\n'
         'if you want to start the server, follow the following steps:\n'
         'second use check-services --a to check if all services are available (services means outside support)'
         'third use start-redis --a to create all redis support',
    disable_argcomplete=False
)

"""
    Create Database Command
"""


@cli.command()
@click.option('-drop-first', is_flag=True, default=True,
              help='Drops the current database before creation', type=bool)
def create_db(drop_first: bool = False):
    """
    creates the SQL tables of the program
    you can pass the flag drop_first to first drop the entire database
    """
    if drop_first and prompt_bool('Are you sure you want to drop the table'):
        datastore.drop_all()
        print('database droped')
    datastore.create_all()
    print('database created successfully')


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
        if use_debugger is None:
            use_debugger = app.debug
            if use_debugger is None:
                use_debugger = True
        if use_reloader is None:
            use_reloader = (not app.debug) or app.config.get('WERKZEUG_RUN_MAIN', None) == 'true'
        sio.run(
            app,
            host=host,
            port=port,
            debug=use_debugger,
            use_reloader=use_reloader,
            **self.server_options
        )


class CreateUser(MyCommand):
    """
        command creating a new user in the system
    """
    description = 'create a new user in the system'
    help = 'creates a new user'

    def get_options(self):
        """
        :return: list of all options for the command
        :type: List[Option]
        """
        return (
            Option('--n', '-name', '-username',
                   dest='username',
                   help='username of the new user'),
            Option('--p', '-password', '-pswd',
                   dest='password',
                   help='password of the new user'),
            Option('--m', '-mail', '-addr', dest='mail_address',
                   help='mail address of the new user'),
            Option('--r', '-role', dest='role',
                   help='Role of the new User'),
            Option('--a', '-admin',
                   dest='role', action='store_const', const='common',
                   help='the users\'s role is setted to be admin'),
            Option('--u', '-user',
                   dest='role', action='store_const', const='common',
                   help='the user\'s role is a simple user'
                   ),
            Option('--s', '-superuser',
                   dest='role', action='store_const', const='common',
                   help='the user\'s role is a superuser, highest rank')
        )

    def run(self, username, password, mail_address, role):
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
        if neither values didnt passed the command parses them
        runs a command to create new user
        """
        if username is None:
            username = prompt('enter a username address of the user\n[username]')
        if password is None:
            password = prompt('you forgeot entering a password, pless enter 1\nPassword: ')
        if mail_address is None:
            mail_address = prompt('enter a mail address of the user\nMail:')
        if role is None:
            # select choices
            role = prompt_choices(
                'You must pick a role, if not default is superuser\n',
                [
                    ('admin', 'admin'),
                    ('a', 'admin'),
                    ('user', 'common'),
                    ('u', 'common'),
                    ('c', 'common'),
                    ('common', 'common'),
                    ('superuser', 'superuser'),
                    ('s', 'superuser')
                ],
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
                password=password,
                email=mail_address,
                role=role_matched
            )
            # save user
            datastore.session.add(user)
            datastore.session.commit()
            print('user created successfully')


class CeleryWorker(Command):
    """Starts the celery worker."""
    capture_all_args = True
    help = 'Start mail celery worker'

    def run(self, argv):
        """
        :param argv: string arguments
        :type argv: List[str]
        :return: None
        runs a celery worker
        """
        ret = subprocess.call(
            ['venv/scripts/celery.exe', 'worker',
             '-A', 'painter.tasks.mail_worker.celery', '-P', 'eventlet'] + argv
        )
        sys.exit(ret)


# adding command
manager.add_command('celery-mail', CeleryWorker)
manager.add_command("create-user", CreateUser())


# drop database
def drop_db():
    if prompt_bool('Are you sure to drop the database'):
        datastore.drop_all()
        print('You should create a new superuser, see create-user command')


drop_database_command = MyCommand(drop_db, 'drops the database entirely')
manager.add_command('drop-db', drop_database_command)

"""
 Check Service Command
 Command to check if services required for the app are working
"""


def check_redis_service(option_flags: FrozenSet[str]) -> Dict[str, Any]:
    """
    :param option_flags: option flags to check
    :return: redis-service response data
    --name
    --status
    --time taken to execute
    """
    result = False
    duration = 'None'
    try:
        if DURATION_OPTION_FLAG in option_flags:
            current_time = time.time()
            redis.ping()
            duration = time.time() - current_time
        else:
            redis.ping()
        if PRINT_OPTION_FLAG in option_flags:
            print('Successfully ping to redis')
        result = True
    except redis_exception.AuthenticationWrongNumberOfArgsError:
        if PRINT_OPTION_FLAG in option_flags:
            print('Cannot Auth to redis, check your password again')
    except redis_exception.TimeoutError:
        if PRINT_OPTION_FLAG in option_flags:
            print('redis timeout, cannot connect to redis server')
    except redis_exception.ConnectionError:
        if PRINT_OPTION_FLAG in option_flags:
            print('Connection closed by server, it must be because')
    except Exception as e:
        print(repr(e))
    finally:
        return {
            'service_name': 'redis',
            'result': 'Connected' if result else 'Error',
            'duration': duration if DURATION_OPTION_FLAG else 'None'
        }


def check_sql_service(option_flags: FrozenSet[str]) -> Dict[str, Any]:
    """
    :param option_flags: option flags to check
    :return: sql database-service response data
    --name
    --status
    --time taken to execute
    """
    result = False
    duration = 'None'
    try:
        # connection
        if DURATION_OPTION_FLAG in option_flags:
            current_time = time.time()
            datastore.engine.connect()
            duration = time.time() - current_time
        else:
            datastore.engine.connect()
        if PRINT_OPTION_FLAG in option_flags:
            print('Successfully connected to sql')
        result = True
    except Exception as e:
        print("Fail to connect to SQL Alchemy")
        raise e
    finally:
        return {
            'service_name': 'SQL',
            'result': 'Connected' if result else 'Error',
            'duration': duration if DURATION_OPTION_FLAG else 'None'
        }


def check_services(all_flag=False, redis_flag=None, sql_flag=None, option_flags=False):
    """
    :param all_flag: boolean flag to check if get all services or none
    :type  all_flag: bool
    (if a flag is set and this is set there dont check service)
    :param redis_flag: flag if to check the redis service
    :type  redis_flag: bool
    :param redis_flag: flag if to check the sql service
    :type  redis_flag: bool
    :param option_flags: option flags, include print and check time of response
    :type  options_flags: Union[str, bool]
    :return: if services are active
    """
    # if in the future I should add other flags
    # check if all of them are None
    option_flags = parse_service_options(option_flags)
    # if all of them are None, check them all
    redis_flag = check_service_flag(redis_flag, all_flag)
    results = []
    # redis check
    if redis_flag:
        # time check
        print('checks if can connect to redis')
        # try with redis
        results.append(check_redis_service(option_flags))
    # check sqlite
    sql_flag = check_service_flag(sql_flag, all_flag)
    # redis check
    if sql_flag:
        # time check
        print('checks if can connect to sql')
        # try with redis
        results.append(check_sql_service(option_flags))
    # print all
    enabled_contexts = tuple(filter(
        lambda option_context: option_context.is_option_enabled(option_flags),
        SERVICE_RESULTS_FORMAT
    ))
    # get result format for contexts
    result_format = '|'.join(context.string_format for context in enabled_contexts)
    print(result_format.format(*[context.title for context in enabled_contexts]))
    for result in results:
        print(result_format.format(*[str(result[context.key]) for context in enabled_contexts]))


check_services_command = Command(check_services)
check_services_command.__dict__['description'] = 'check if services the app uses are active,' \
                                                 'there are currently 1: redis'
check_services_command.add_option(Option(
    '--r', '-redis', dest='redis_flag', action='store_true', help='to check update with redis'
))
check_services_command.add_option(Option(
    '--s', '-sql', dest='sql_flag', action='store_true', help='to check update with sqlalchemy'
))
check_services_command.add_option(Option(
    '--a', '-all', dest='all_flag', action='store_true', help='to check update with all'
))
check_services_command.add_option(Option(
    '--o', '-options', nargs='*', dest='option_flags', default=True,
    help='special options for the command: t for display the time it takes to end and'
))
manager.add_command('check-services', check_services_command)


# work on this
def redis_database(board_operator=None, lock_operator=None, apply_all=None):
    """
    :param board_operator: operation with the board object
    :param lock_operator: operation with the lock object
    :return:
    operators avilage:
    --reset: reset data: create and remove
    --delete: entirely remove data
    --create: create data
    """
    # check redis
    board_operator = board_operator if board_operator is not None else apply_all
    lock_operator = lock_operator if lock_operator is not None else apply_all
    if board_operator is None and lock_operator is None:
        raise InvalidCommand('You must enter any value')
    try:
        redis.ping()
        print('Redis Works')
    # exception
    except Exception as e:
        print('While Checking Redis encouter error')
        print(repr(e))
        return
        # try
    if board_operator is not None:
        try:
            if board_operator == 'reset' and prompt_bool('Are you sure you want to reset the board?'):
                board.drop_board()
                board.make_board()
                print('Board reset successfully')
            elif board_operator == 'create':
                if not board.make_board():
                    print('board already created, use reset or drop to clear board')
                else:
                    print('Board created successfully')
            elif board_operator == 'drop':
                if not board.drop_board():
                    print('Error while dropping board')
                else:
                    print('Board dropped successfully')
        except Exception as e:
            print(repr(e))
    if lock_operator is not None:
        try:
            if lock_operator == 'reset':
                if not lock.drop_lock():
                    print('Lock doesnt exists, create it using create command')
                else:
                    lock.create_lock()
                    print('Lock reset successfully')
            elif lock_operator == 'create':
                if not lock.create_lock():
                    print('Lock already created, use reset or drop to clear board')
                else:
                    print('Lock deleted successfully')
            elif lock_operator == 'drop':
                if not lock.drop_lock():
                    # error print
                    print('Lock doesnt exists')
                else:
                    # success
                    print('Lock deleted successfully')
        except Exception as e:
            print(repr(e))
    print('command finishes')


redis_database_command = MyCommand(
    redis_database,
    description='function to work with the redis objects\n'
                'args options:\n'
                '\treset:\t\tresets the value and recreated is'
                '\tdrop:\t\tdrops the key and remove it from the database'
                '\tcreate:\t\tcreated the key in the database'
)
redis_database_command.add_option(Option(
    '--b', '-board', dest='board_operator',
    help='options with lock',
    choices=['reset', 'drop', 'create']
))
redis_database_command.add_option(Option(
    '--l', '-lock', dest='lock_operator', help='options with lock',
    choices=['reset', 'drop', 'create'], default='reset'
))
redis_database_command.add_option(Option(
    '--a', '-all', dest='apply_all', help='options with all variables',
    choices=['reset', 'drop', 'create'], default='create'
))

manager.add_command('redis', redis_database_command)


def clear_cache():
    """
        clears all unused cache of storage models
    """
    for model_class in ExpireModels:
        model_class.clear_cache(False)
    datastore.session.commit()
    print('Clear Cache Complete')


# adds clear cache command
manager.add_command('clear-cache', Command(clear_cache))
