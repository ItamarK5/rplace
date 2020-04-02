from sys import argv
from painter import create_app


if __name__ == '__main__':
    app, sio, celery = create_app()
    sio.run(
        app=app,
        debug=True,
        host='0.0.0.0',
        port=int(argv[1]) if len(argv) > 1 else 8080,
    )

#  celery -A proj worker -P eventlet -c 1000
