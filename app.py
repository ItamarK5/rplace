from sys import argv

from painter.app import run_socketio

if __name__ == '__main__':
    run_socketio(
        debug=True,
        host='0.0.0.0',
        port=int(argv[1]) if len(argv) > 1 else 8080,
    )

#  celery -A proj worker -P eventlet -c 1000
