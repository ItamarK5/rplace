from painter import *

if __name__ == '__main__':
    db.create_all(app=app)
    sio.run(
        app,
        debug=True,
        host='0.0.0.0',
        port=8080,
    )
