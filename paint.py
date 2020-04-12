"""
Author: Itamar Kannne
Main App
"""
import sys
from painter.manager import manager
from flask_script.commands import InvalidCommand

if __name__ == '__main__':
    try:
        manager.run()
    except InvalidCommand as err:
        # prints
        print(err, file=sys.stderr)
        sys.exit(1)
