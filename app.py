import sys
from painter.manager import manager
from flask_script.commands import InvalidCommand

if __name__ == '__main__':
    try:
        manager.run()
    except InvalidCommand as err:
        print(err, file=sys.stderr)
        sys.exit(1)
#  celery -A proj worker -P eventlet -c 1000
