"""
Auther: Itamar Kanne
the manager module decorates the app by command line parameter
the module is based of flask_script module
https://flask-script.readthedocs.io/en/latest/
"""
import sys
import subprocess
from .app import app, sio, datastore
from flask_script import Manager, Server, Option, Command
from flask import Flask
from typing import Optional
from .models.role import Role
from

manager = Manager(app)


# https://github.com/miguelgrinberg/flack/blob/master/manage.py
class Start(Server):
    """
    The Start Server Command
    the function get the following parameters:
    ;host: the host to start the server
    ;port: the port to start the server
    ;local: the
    """

    help = description = 'Runs the server'

    def get_options(self):
        options = (
            Option('-h', '--host',
                   dest='host',
                   default='0.0.0.0',
                   help=('host url of the server')),
            Option('-p', '--port',
                   dest='port',
                   type=int,
                   default=8080,
                   help=('host port of the server')),
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

    def __call__(self, app, host ,port, use_debugger, use_reloader):
        # override the default runserver command to start a Socket.IO server
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

@manager.option('--n', '-name', dest="name", help='name of the new user', required=True)
@manager.option('--p', '-password', dest="name", help='password of the new user', required=True)
@manager.option('--e', '-email', dest="name", help='email of the new user', required=True)
@manager.option('--r', '-role', dest='role', help='Role of the new user, default admin')
def add_user():


@manager.option()
@manager.command
def createdb(drop_first=False):
    if drop_first:
        datastore.drop_all()
    datastore.create_all()


class CreateUser(Command):
    help = description = 'create a new user in the database'

    def add_option(self, option):

    def run(self, name, password, email, role='admin'):
        # first decide between roles
        if reNAME





class CeleryWorker(Command):
    """Starts the celery worker."""
    name = 'celery'
    capture_all_args = True

    def run(self, argv):
        ret = subprocess.call(
            ['celery', 'worker', '-A', 'painter.celery', '-P', 'eventlet', '-l'] + argv)
        sys.exit(ret)


manager.add_command('celery', CeleryWorker)
manager.add_command("runserver", Start())