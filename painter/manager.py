import sys
import subprocess
from .app import app, sio, datastore
from flask_script import Manager, Server, Option, Command
from flask import Flask
from typing import Optional

manager = Manager(app)


# https://github.com/miguelgrinberg/flack/blob/master/manage.py
class Start(Server):
    def run(self):
        self()

    help = description = 'Runs the server'

    def get_options(self):
        options = (
            Option('-h', '--host',
                   dest='host',
                   default='0.0.0.0'),
            Option('-p', '--port',
                   dest='port',
                   type=int,
                   default=8080),
            Option('-d', '--debug',
                   action='store_true',
                   dest='use_debugger',
                   help=('enable the Werkzeug debugger (DO NOT use in '
                         'production code)'),
                   default=self.use_debugger),
            Option('-D', '--no-debug',
                   action='store_false',
                   dest='use_debugger',
                   help='disable the Werkzeug debugger',
                   default=self.use_debugger),

            Option('-r', '--reload',
                   action='store_true',
                   dest='use_reloader',
                   help=('monitor Python files for changes (not 100%% safe '
                         'for production use)'),
                   default=self.use_reloader),
            Option('-R', '--no-reload',
                   action='store_false',
                   dest='use_reloader',
                   help='do not monitor Python files for changes',
                   default=self.use_reloader),
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


@manager.command
def createdb(drop_first = False):
    if drop_first:
        datastore.drop_all()
    datastore.create_all()


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