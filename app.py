from sys import argv

from painter import app, sio

if __name__ == '__main__':
    sio.run(
        app,
        debug=True,
        host='192.168.1.10',
        port=argv[1] if len(argv) > 1 else 8080,
    )

#  celery -A proj worker -P eventlet -c 1000
