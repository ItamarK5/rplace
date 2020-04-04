"""
Auther: Itamar Kanne
the manager module decorates the app by command line parameter
the module is based of flask_script module
https://flask-script.readthedocs.io/en/latest/
"""
import subprocess
import sys
import os
from flask_script import Manager, Server, Option, Command
from flask_script.cli import prompt_bool, prompt_choices, prompt
from flask_script.commands import InvalidCommand
from .app import create_app, datastore, sio
from .models.role import Role
from .models.user import User
from .others.manager_utils import NewUserForm, PAINTER_ENV_NAME, add_configure



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
                   default='0.0.0.0',
                   help='host url of the server'),
            Option('-p', '--port',
                   dest='port',
                   type=int,
                   default=8080,
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
        :type   use_debugger: Boolean
        :param  use_reloader: use
        :return: nothing
        override the default runserver command to start a Socket.IO server
        """
        if use_debugger is None:
            use_debugger = app.debug
            if use_debugger is None:
                use_debugger = True
        if use_reloader is None:
            use_reloader = app.debug
        sio.run(
            app,
            host=host,
            port=port,
            debug=use_debugger,
            use_reloader=use_reloader,
            **self.server_options
        )


manager = Manager(create_app)
manager.add_option('--c', '-config', dest='config', default='config.py', required=False)


@manager.option('--d', '-drop', dest='drop-first', help='drop before creating app', default=True)
def create_db(drop_first=False):
    if drop_first and prompt_bool('Are you sure you want to drop the table'):
        datastore.drop_all()
    datastore.create_all()


@manager.command
def drop_db():
    if prompt_bool('Are you sure to drop the database'):
        datastore.drop_all()
        print('You should create a new superuser')


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


manager.add_command('celery', CeleryWorker)
manager.add_command("runserver", RunServer())
manager.add_command("create-user", CreateUser())

