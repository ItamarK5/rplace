"""
    Author: Itamar Kanne

    the manager module decorates the app by command line parameter
    first I use the flask script module
    the module is based of flask_script module
    https://flask-script.readthedocs.io/en/latest/
    but then I used the click and flask.cli
"""
import subprocess
import sys
import time
from typing import Iterable, Any, Dict, FrozenSet, Optional

import click
import flask.cli
from flask import current_app
from redis import exceptions as redis_exception
# first import app to prevent some time related import bugs
from .app import datastore, sio, redis as redis_ext, create_app
from .backends import board, lock
from .models import ExpireModels, User, Role
from .others.constants import (
    DURATION_OPTION_FLAG, PRINT_OPTION_FLAG,
    SERVICE_RESULTS_FORMAT, REDIS_DATABASE_OPERATIONS,
    ROLE_CHOICE_MAP
)
from .others.utils import (
    parse_service_options, check_service_flag, prompt_are_you_sure,
    abort_if_false, QuickEmailForm, QuickPasswordForm, QuickUsernameForm,
    FormValidateType, ChoiceMap
)
import time
t = time.time()

cli = flask.cli.FlaskGroup(
    create_app=create_app,
    add_default_commands=False,
    help='Social Painter CMD Service\n'
         'if you want to start the server, follow the following steps:\n'
         'second use check-services --a to check if all services are '
         'available (services means outside support) third '
         'use start-redis --a to create all redis support'
)


@cli.command(name="run", short_help="Run a development server.")
@click.option("--host", "-h", default=None, help="The interface to bind to.")
@click.option("--port", "-p", default=None, help="The port to bind to.")
# if to use the reload option
@click.option(
    "--reload/--no-reload",
    default=None,
    help="Enable or disable the reloader. By default the reloader "
         "is active if debug is enabled.",
)
# if to use the debugger
@click.option(
    "--debugger/--no-debugger",
    default=None,
    help="Enable or disable the debugger. By default the debugger "
         "is active if debug is enabled.",
)
@flask.cli.pass_script_info
def run_server(
        info: flask.cli.ScriptInfo,
        host: Optional[str] = None,
        port: Optional[int] = None,
        reload: Optional[bool] = None,
        debugger: Optional[bool] = None,
) -> None:
    """Run a local development server.

    This server is for development purposes only. It does not provide
    the stability, security, or performance of production WSGI servers.

    The reloader and debugger are enabled by default if
    FLASK_ENV=development or FLASK_DEBUG=1.
    """
    """
        overrides the default 
    """
    host = host if host else current_app.config.get('APP_HOST', '127.0.0.1')
    if host == 'local-router':
        # try get router
        # https://stackoverflow.com/a/166520
        try:
            import socket
            host = socket.gethostbyname(socket.gethostname())
        finally:
            # if host didnt change
            if host == 'local-router':
                host = '127.0.0.1'

    port = port if port else current_app.config.get('APP_PORT', 5000)
    debug = flask.cli.get_debug_flag()  # get debug flag
    if reload is None:
        # reloading
        reload = reload

    if debugger is None:
        # if debugger isn't set, use debug
        debugger = debug
    print(time.time()-t)
    sio.run(
        info.load_app(),
        host,
        port,
        use_reloader=reload,
        debug=debugger or True,  # if to use the debugger
        threaded=True
    )


@cli.command(name='create-user')
@click.option('-n', '--name', '--username', required=True,
              help='username of the new user', type=FormValidateType('username', QuickUsernameForm))
@click.option('-p', '-pswd', '--password', required=True,
              help="password of the new user", type=FormValidateType('password', QuickPasswordForm))
@click.option('-m', '--mail', required=True,
              help='mail address of the new user', type=FormValidateType('mail_address', QuickEmailForm))
@click.option('--r', '-role', required=True,
              help='Role of the new User', type=ChoiceMap(ROLE_CHOICE_MAP))
def create_user(username: str, password: str, mail_address: str, role: Role) -> None:
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
    # create user
    user = User(
        username=username,
        password=password,
        email=mail_address,
        role=role
    )
    # save user
    datastore.session.add(user)
    datastore.session.commit()
    print('user created successfully')


@cli.command('worker', help='Starts mail celery worker')
@click.argument('name', required=False, default='0', nargs=1)
@click.argument('args', nargs=-1)
def celery_worker(name: str, args: Iterable[Any]) -> None:
    """
    :param name: the name of the worker to
    :param args: arguments to call with the celery worker
    :return: using the subprocess module calls the celery worker
    """
    name_args = [] if not name else ['-n', name]
    celery_process = subprocess.call(
        ['venv/scripts/celery.exe', 'worker',
         '-A', 'painter.tasks.worker.celery', '-P', 'eventlet']
        + name_args
        + list(args)
    )
    sys.exit(celery_process)


# create database
@cli.command(
    name="create-db",
    short_help="creates the SQL tables of the program",
    help="creates the SQL tables of the program\n"
         "you can pass the flag drop_first to first drop the entire database"
)
@click.option('-drop-first', is_flag=True, default=False,
              help='Drops the current database before creation', type=bool,
              prompt='Are you sure you want to drop the table')
@click.pass_context
def create_db(ctx: click.Context, drop_first: bool = False):
    """
    :param ctx: the flask.cli context
    :param drop_first: if to drop all database before creating
    """
    if drop_first and prompt_are_you_sure(ctx, 'Are you sure you want to drop the board?'):
        datastore.drop_all()
        print('database droped')
    datastore.create_all()
    print('database created successfully')


# drop database
@cli.command('drop-db', help='drops the database entirely')
@click.confirmation_option('--yes', is_flag=True, callback=abort_if_false,
                           expose_value=False,
                           prompt='Are you sure you want to drop the db?')
def drop_db():
    """
    :return: Drops the database
    """
    if click.prompt('Are you sure to drop the database'):
        datastore.drop_all()
        print('You should create a new superuser, see create-user command')


"""
 Check Service Command
 Commands to check if services required for the app are working
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
            redis_ext.ping()
            duration = time.time() - current_time
        else:
            redis_ext.ping()
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


@cli.command(
    name='check-services',
    short_help='check if services related to the are active and can connect to them',
    help="You can also set optional flags for the parameter:\n"
         "\ttimestamp:"
         "\t"
)
@click.option(
    '-all',
    is_flag=True,
    default=False,
    required=False,
    help='flag, if set the command checks all options expect those who were given',
)
@click.option(
    '-redis',
    is_flag=True,
    default=False,
    required=False,
    help='to check if the redis server is active'
)
@click.option(
    '-s', '--sql',
    is_flag=True,
    default=False,
    type=click.types.BOOL,
    required=False,
    help='to check if the sql server is active'
)
@click.option(
    '--options',
    default=None,
    required=False,
    help='Optional flags to set'
)
@click.option(
    '-all-options',
    is_flag=True,
    default=False,
    required=False,
    help="select all optional flags"
)
def check_services(all: bool = False, redis: bool = False, sql: bool = False,
                   options: Optional[str] = None, all_options: bool = False) -> None:
    """
    :param all: boolean flag to check if get all services or none
    (if a flag is set and this is set there don;t check service)
    :param redis: flag if to check the redis service
    :param sql: flag if to check the sql service
    :param options: option flags, include print and check time of response
    :param all_options: if to select all options available
    :return: if services are active
    """
    # if all flags are cleared : nothing happend
    # also if they all set, all flags negate all flag
    if sql == redis == all:
        raise click.UsageError("You must set at least one flag something"
                               if not all else "You must remove at least 1 flag, you cant set them all")
    # if in the future I should add other flags
    # check if all of them are None
    option_flags = parse_service_options(None if not options else options.split(','), all_options)
    # if all of them are None, check them all
    redis_flag = check_service_flag(redis, all)
    results = []
    # redis check
    if redis_flag:
        # time check
        print('checks if can connect to redis')
        # try with redis
        results.append(check_redis_service(option_flags))
    # check sqlite
    sql_flag = check_service_flag(sql, all)
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


@cli.command(
    name='redis',
    help='function to work with the redis objects\n'
         'choices for options:\n'
         '\treset:\t\tresets the value and recreated is'
         '\tdrop:\t\tdrops the key and remove it from the database'
         '\tcreate:\t\tcreated the key in the database'
)
@click.option(
    '-b', '-board',
    help='clear/create/reset board value in database',
    required=False,
    default=None,
    type=REDIS_DATABASE_OPERATIONS,
)
@click.option(
    '-l', '--lock',
    help='clear/create/reset lock value in database',
    required=False,
    default=None,
    type=REDIS_DATABASE_OPERATIONS,
)
@click.pass_context
def redis_database(ctx: click.Context, board_operator: str = None, lock_operator: str = None, apply_all: str = None):
    """
    :param ctx: context of flask.cli
    :param board_operator: operation with the board object
    :param lock_operator: operation with the lock object
    :param apply_all: apply to both objects
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
        raise click.UsageError('You must enter any value')
    try:
        redis_ext.ping()
        print('Redis Works')
    # exception
    except Exception as e:
        print('While Checking Redis encounter error')
        print(repr(e))
        return
        # try
    if board_operator is not None:
        try:
            # try get the board
            if board_operator == 'reset' and prompt_are_you_sure(ctx, 'Are you sure you want to reset the board?'):
                board.drop_board()
                board.make_board()
                print('Board reset successfully')
            elif board_operator == 'create':
                if not board.make_board():
                    print('board already created, use reset or drop to clear board')
                else:
                    print('Board created successfully')
            elif board_operator == 'drop' and prompt_are_you_sure(ctx, "are you sure you want to drop the board"):
                if not board.drop_board():
                    print('Error while dropping board')
                else:
                    print('Board dropped successfully')
        except Exception as e:
            print(repr(e))
    if lock_operator is not None:
        try:
            # reset operation
            if lock_operator == 'reset':
                if not lock.drop_lock():
                    print('Lock doesnt exists, create it using create command')
                else:
                    lock.create_lock()
                    print('Lock reset successfully')
            # create operation
            elif lock_operator == 'create':
                if not lock.create_lock():
                    print('Lock already created, use reset or drop to clear board')
                else:
                    print('Lock deleted successfully')
            # drop operation
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


@cli.command(
    name='clear-cache',
    help='Clears cache that expired'
)
def clear_cache():
    """
        clears all unused cache of storage models
    """
    for model_class in ExpireModels:
        model_class.clear_cache(False)
    datastore.session.commit()
    print('Clear Cache Complete')