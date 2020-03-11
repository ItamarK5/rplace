from sys import argv
from painter import *

if __name__ == '__main__':
    sio.run(
        app,
        debug=True,
        host='0.0.0.0',
        port=argv[1],
    )
