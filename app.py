from painter import *

if __name__ == '__main__':
    db.create_all(app=app)
    sio.run(app,
            host='localhost',
            port=80,
            debug=True,
            # keyfile='https\\key.pem',
            # certfile='https\\cert.pem'
    )
