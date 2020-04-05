"""
Auther: Itamar Kanne
the manager module decorates the app by command line parameter
the module is based of flask_script module
https://flask-script.readthedocs.io/en/latest/
"""
import subprocess
import sys
from flask_script import Manager, Server, Option, Command
from flask_script.cli import prompt_bool, prompt_choices, prompt
from flask import current_app
from flask_script.commands import InvalidCommand
from .app import create_app, datastore, sio
from .models.role import Role
from .models.user import User
from .others.utils import NewUserForm, check_isfile, PortQuickForm,\
    IPv4QuickForm, try_save_json, try_load_json, CONFIG_FILE_PATH_KEY, try_save_json
from configparser import ConfigParser


manager = Manager(create_app)
manager.add_option('--c', '-config', dest='config_path', required=False)
manager.add_option('--D', '-default', dest='set_env', action='store_true')
manager.add_option('--t', '-title', dest='title')


class RunServer(Server):
    """
    source: https://github.com/miguelgrinberg/flack/blob/master/manage.py
    auther: miguelgrinberg
    edited by me
    The Start Server Command
    the function get the following parameters:
    host: the host to start the server
    port: the port to start the server
    """

    help = description = 'Runs the server'

    def get_options(self):
        options = (
            Option('-h', '--host',
                   dest='host',
                   default=None,
                   help='host url of the server'),
            Option('-p', '--port',
                   dest='port',
                   type=int,
                   default=None,
                   help='host port of the server'),
            Option('-d', '--debug',
                   action='store_true',
                   dest='use_debugger',
                   help=('enable the Werkzeug debugger (DO NOT use in '
                         'production code)'),
                   default=self.use_debugger),  # True
            Option('-D', '--no-debug',
                   action='store_false',
                   dest='use_debugger',
                   help='disable the Werkzeug debugger',
                   default=self.use_debugger),  # False
            Option('-r', '--reload',
                   action='store_true',
                   dest='use_reloader',
                   help=('monitor Python files for changes (not 100%% safe '
                         'for production use)'),
                   default=self.use_reloader),  # True
            Option('-R', '--no-reload',
                   action='store_false',
                   dest='use_reloader',
                   help='do not monitor Python files for changes',
                   default=self.use_reloader),  # False
        )
        return options

    def __call__(self, app, host, port, use_debugger, use_reloader):
        """
        :param  host: host the ip to run the server
        :type:  host: int
        :param  port: port to listen on the ip
        :type   port: int
        :param  use_debugger: if to use debbugger while running the application
        :type   use_debugger: bool
        :param  use_reloader: if to use the reloader option of flask
        :type   user_debugger: bool
        :return: nothing
        override the default runserver command to start a Socket.IO server
        """
        host = host if host is not None else app.config.get('APP_HOST', '127.0.0.1')
        port = port if port is not None else app.config.get('APP_PORT', 8080)
        print(host, port)
        if use_debugger is None:
            use_debugger = app.debug
            if use_debugger is None:
                use_debugger = True
        if use_reloader is None:
            use_reloader = not app.debug and app.config.get('WERKZEUG_RUN_MAIN')
        print(app.config)
        sio.run(
            app,
            host=host,
            port=port,
            debug=use_debugger,
            use_reloader=use_reloader,
            **self.server_options
        )


class CreateUser(Command):
    description = 'create a new user in the system'
    help = 'creates a new user'

    def get_options(self):
        return (
            Option('--n', '-name', '-username',
                   dest='username',
                   help='name of the new user'),
            Option('--p', '-password', '-pswd',
                   dest='password',
                   help='password of the new user'),
            Option('--m', '-mail', '-addr', dest='mail_address',
                   help='mail address of the new user'),
            Option('--r', '-role', dest='role',
                   help='Role of the new User'),
            Option('--a', '-admin', dest='role',
                   help='the users\'s role is setted to be admin'),
            Option('--u', '-user',
                   dest='role', default='user',
                   help='the user\'s role is a simple user'
                   ),
            Option('--s', '-superuser',
                   dest='role', default='superuser',
                   help='the user\'s role is a superuser, highest rank')
        )

    def run(self, username, password, mail_address, role):
        if username is None:
            username = prompt('enter a username address of the user\nUsername: ')
        if password is None:
            password = prompt('you forgeot entering a password, pless enter 1\nPassword: ')
        if mail_address is None:
            mail_address = prompt('enter a mail address of the user\nMail:')
        if role is None:
            role = prompt_choices(
                'You must pick a role, if not default is superuser',
                (
                    ('admin', 'admin'),
                    ('a', 'admin'),
                    ('user', 'user'),
                    ('u', 'user'),
                    ('superuser', 'superuser'),
                    ('s', 'superuser')
                ),
                'superuser'
            )
        role_matched = Role.get_member_or_none(role)
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
            datastore.session.add(user)
            datastore.session.commit()
            print('user created successfully')


class CeleryWorker(Command):
    """Starts the celery worker."""
    name = 'celery'

    def run(self):
        ret = subprocess.call(
            ['venv/scripts/celery.exe', 'worker', '-A', 'painter.celery_worker.celery', '-P', 'eventlet']
        )
        sys.exit(ret)


# adding command
manager.add_command('celery', CeleryWorker)
manager.add_command("runserver", RunServer())
manager.add_command("create-user", CreateUser())

"""
def set_config(file_path, num=None):
    if (not os.path.exists(file_path)) or os.path.isdir(file_path):
        raise InvalidCommand("No file exists at: {0}".format(file_path))
    # check environment
    if PAINTER_ENV_NAME not in os.environ:
        if num is None:
            os.environ[PAINTER_ENV_NAME] = file_path
        else:
            raise InvalidCommand("Cannot Access specific the painter path, so number dont matther")
    else:
        # add second
        os.environ[PAINTER_ENV_NAME] = add_configure(os.environ.get(PAINTER_ENV_NAME), file_path, num)
        print('Finished, Added Config File to environment')


set_config = Command(set_config)
set_config.add_option(Option('--p', '-path', dest='file_path'))
set_config.add_option(Option('--n', '-num', dest='num', default=None))
manager.add_command('set-config', set_config)
"""


def create_db(drop_first=False):
    if drop_first and prompt_bool('Are you sure you want to drop the table'):
        datastore.drop_all()
    datastore.create_all()


create_db_command = Command(
    create_db,
)
#create_db_command.help_args = 'creates the database'
create_db_command.add_option(
    Option('--d', '-drop', dest='drop-first',
           action='store_true', default=False,
           help='Drops the current database before creation')
)
manager.add_command('create-db', create_db_command)


# drop database
def drop_db():
    if prompt_bool('Are you sure to drop the database'):
        datastore.drop_all()
        print('You should create a new superuser, see create-user command')


drop_databse_command = Command(drop_db)
# drop_databse_command.help_args = ('drops the database entirely',)
manager.add_command('drop-db', drop_databse_command)


def add_config(name=None, host=None, port=None):
    # name in save mode
    name = name.upper().replace(' ', '_')
    # get file
    config_path = current_app.config[CONFIG_FILE_PATH_KEY]
    error_text = check_isfile(config_path)
    if error_text is not None:
        raise InvalidCommand(error_text)
    # validate the port and host
    # read file
    # try load
    configuration = try_load_json(config_path)
    if name in configuration:
        raise InvalidCommand('Configure Option {0} already exists'.format(name))
    # else get host and port
    # if passed any arguments => didn't pass both None
    if host is not None or port is not None:
        is_host_valid = host is None or IPv4QuickForm.are_valid(address=host)
        is_port_valid = port is None or PortQuickForm.are_valid(port=port)
        if not (is_host_valid or is_port_valid):
            raise InvalidCommand('Invalid Host and Port:{0}:{1}'.format(host, port))
        elif not is_host_valid:
            raise InvalidCommand('Invalid Host: {0}'.format(host))
        elif not is_port_valid:
            raise InvalidCommand('Invalid Port: {0}'.format(port))
    # parse if neither is None
    if host is None:
        is_valid = IPv4QuickForm.are_valid(address=host)
        while not is_valid:
            # after first parse
            host = prompt('Pless enter a valid IPv4 Address\n[HOST]')
            print(len(host))
            form, is_valid = IPv4QuickForm.fast_validation(address=host)
            if not is_valid:
                form.error_print()
    # validate port
    if port is None:
        is_valid = isinstance(port, str) and port.isdigit() and PortQuickForm.are_valid(port=port)
        while not is_valid:
            # after first parse
            port = prompt('Pless enter a valid Port [0-65536]\n[PORT]')
            if not port.isdigit():
                print('Port must be a number')
                # dont validate because it still as before, false
            else:
                # check form now it knows that port cannot be a number
                form, is_valid = PortQuickForm.fast_validation(port=int(port))
                if not is_valid:
                    form.error_print()
    # add the configure
    configuration[name] = {
        'APP_HOST': host,
        'APP_PORT': int(port)
    }
    # save configuration
    try_save_json(configuration, config_path)
    print('Configuration {0} Created'.format(name))


create_config_command = Command(add_config)
create_config_command.add_option(
    Option('--h', '-host', dest='host', default=None, required=False,
           help="Host/The IP Address of the server, default 127.0.0.1 (localhost), if no app configuration exist"),
)
create_config_command.add_option(
    Option('--p', '-port', dest='port', default=None, required=False,
           help="Port the server listens to default is 8080 if no app configuration is passed")
)
create_config_command.add_option(
    Option('--n', '-name', dest='name',
           help="Port the server listens to default is 8080 if no app configuration is passed")
)
manager.add_command('add-config', create_config_command)


def del_config(key=None):
    pass

def remove_config(name=None):
    parser = ConfigParser()
    with parser.read_file as rfile:
        pass
    pass


def get_config(name) -> None:
    pass
