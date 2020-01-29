from painter import *
from flask import Flask
from threading import Thread

if __name__ == '__main__':
    Thread(target=save_board).start()
    sio.run(app, host='0.0.0.0', port=8080, debug=True)
