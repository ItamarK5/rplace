from painter import *

if __name__ == '__main__':
    start_save_board()
    db.create_all(app=app)
    sio.run(app, host='0.0.0.0', port=8080, debug=True)
