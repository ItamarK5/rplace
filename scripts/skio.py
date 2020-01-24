from flask_socketio import SocketIO as FSkio
import os
import numpy as np
sio = FSkio()
board = np.ndarray()

def open_board() -> np.ndarray()
    #  save board
    print(os.path.exists(r'resources\img.npy'))
    if os.path.exists(r'resources\img.npy'):
        place_board = np.load(r'..\\resources\img.npy')
        print(place_board.shape)
    else:
        place_board = np.zeros((1000, 500), dtype=np.uint8)
        # board = np.random.randint(0, 255, (1000, 500), np.uint8) - used for testing
    return place_board


"""
code from the past
import socketio
import asyncio
import aiosqlite
import numpy as np
from aiohttp_security import forget, authorized_userid
from typing import Union, Coroutine, Dict
import time
from datetime import datetime, timedelta
from scripts.consts import *

MIN_COOLDOWN = timedelta(minutes=5)


def open_board():
    
        save board
    import os
    print(os.path.exists(r'resources\img.npy'))
    if os.path.exists(r'resources\img.npy'):
        place_board = np.load(r'resources\img.npy')
        print(place_board.shape)
    else:
        place_board = np.zeros((1000, 500), dtype=np.uint8)
        # board = np.random.randint(0, 255, (1000, 500), np.uint8)
    return place_board

def get_static_name(name, path):
    item = {
        'filename': '/' + path, 'content_type': CONTENT_TYPES[name.split('.')[-1]]
    }
    return path, item

static_files = dict(
    [get_static_name(*items) for items in PATHS.items()]
)

board = open_board()    # start board
sio = socketio.AsyncServer(async_mode='aiohttp', async_handlers=True)

@sio.on('set-board')
async def set_board(sid, params: Dict[str, Union[int, str]]) -> None:
    async with sio.session(sid) as session:
        current_time = datetime.now()
        if current_time - session['time'] <= MIN_COOLDOWN:
            await sio.emit('update-timer', str(session['time']+MIN_COOLDOWN), to=sid)
            return
        # validating parameter
        if 'x' not in params or (not isinstance(params['x'], int)) or not (0 <= params['x'] < 1000):
            return
        if 'y' not in params or (not isinstance(params['y'], int)) or not (0 <= params['y'] < 1000):
            return
        if 'color' not in params or (not isinstance(params['color'], int)) or not (0 <= params['color'] < 16):
            return
        x, y, clr = params['x'], params['y'], int(params['color'])
        if x % 2 == 0:
            board[y, x // 2] &= 0xF0
            board[y, x // 2] |= clr
        else:
            board[y, x // 2] &= 0x0F
            board[y, x // 2] |= clr << 4
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute(f'UPDATE Users '
                             f'SET time=\'{current_time.timestamp()}\' '
                             f'WHERE name==\'{session["username"]}\'')
            await db.commit()
            session['time'] = current_time
        await sio.emit('update-timer', str(current_time+MIN_COOLDOWN), to=sid)
        print('emit')
        await sio.emit('set-board', params)


@sio.event
async def connect(sid, environ) -> None:
    username = await authorized_userid(environ['aiohttp.request'])  # get request
    print(username)
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('SELECT (time) FROM Users WHERE name==\'{name}\''.format(name=username)) as cursor:
            last_time_user = await cursor.fetchone()
            if last_time_user is not None:
                await sio.save_session(sid, {
                    'username': username,
                    'time': datetime.fromtimestamp(last_time_user[0])
                })

@sio.on(event='get-first')
async def get_board_status(sid):
    session = await sio.get_session(sid)
    print(session)
    return board.tobytes(), str(session['time']+MIN_COOLDOWN)


@sio.event
async def disconnect(sid) -> None:
    print("connect ", sid)


async def save_board(board: np.ndarray, loop: asyncio.AbstractEventLoop) -> None:
    await asyncio.sleep(10)
    np.save(r'static\img.npy', board)
    loop.create_task(save_board(board, loop))
"""