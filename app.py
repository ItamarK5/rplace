from sys import argv
from painter import app, sio, config
import eventlet
from eventlet import wsgi
if __name__ == '__main__':
    """
    sio.run(
        app,
        debug=True,
        host='0.0.0.0',
        port=argv[1] if len(argv) > 1 else 8080,
    )
    """
    wsgi.server(eventlet.listen(('', int(argv[1]) if len(argv) > 1 else 8080)), app)

#  celery -A proj worker -P eventlet -c 1000
