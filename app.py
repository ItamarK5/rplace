from painter import *


if __name__ == '__main__':
    start_save_board()
    sio.run(app, host='0.0.0.0', port=8080, debug=True)
