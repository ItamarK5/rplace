"""
Author: Itamar Kannne
Main App
"""
import sys
from flask_script.commands import InvalidCommand


if __name__ == '__main__':
    from eventlet import monkey_patch
    # monkey patching for eventlet
    monkey_patch()
    # import staff
    from painter.manager import manager

    # then run manager
    try:
        manager.run()
    except InvalidCommand as err:
        # prints
        print(err, file=sys.stderr)
        sys.exit(1)
