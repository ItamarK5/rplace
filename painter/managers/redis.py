from flask_script import Manager
from flask_script.cli import prompt_bool

from painter.backends import board, lock
from painter.backends.extensions import redis


def try_connect_to_redis() -> bool:
    """
    :return: if connected to redis successfully
    """
    try:
        redis.ping()
        print("redis works")
    except Exception as e:
        print('While Checking Redis encounter error')
        print(repr(e))
        return False
    return True


redis_manager = Manager(help='operations to work with the values stored in the redis server')


@redis_manager.option(
    '--b', '-board', dest='create_board', action="store_true",
    help='create the board in server',
)
@redis_manager.option(
    '--l', '-lock', dest='create_lock', action="store_true",
    help='create the lock in server')
def create(create_board=None, create_lock=None):
    """
    created the objects in the database
    the board flag.
    """
    # first try making the board
    if not (create_lock or create_lock):
        print("You didn't enter anything so creating both")
        create_lock = True
        create_board = True
    if try_connect_to_redis():
        if create_board:
            if not board.create():
                print('board already created, use reset or drop to clear board')
            else:
                print('Board created successfully')
        if create_lock:
            if not lock.create():
                print('Lock already created, use reset or drop to clear board')
            else:
                print('Lock deleted successfully')
    print("Command End")


@redis_manager.option(
    '--b', '-board', dest='drop_board', action="store_true",
    help='drops the lock in the redis server',
)
@redis_manager.option(
    '--l', '-lock', dest='drop_lock', action="store_true",
    help='drops the board in the redis server',
)
def drop(drop_board=None, drop_lock=None):
    """
    drops the objects in the database
    required the board flag or lock flag to
    """
    # first try making the board
    if not (drop_lock or drop_board) and prompt_bool("Are you sure to drop them both?"):
        print("You didn't enter anything so creating both")
        drop_lock = True
        drop_board = True
    # try connect
    if try_connect_to_redis():
        if drop_board:
            if not board.drop():
                print('Error while dropping board')
            else:
                print('Board dropped successfully')
        if drop_lock:
            if not lock.create():
                print('Lock already created, use reset or drop to clear board')
            else:
                print('Lock deleted successfully')
    print("Command End")


@redis_manager.option(
    '--b', '-board', dest='reset_board', action="store_true",
    help='options with lock')
@redis_manager.option(
    '--l', '-lock', dest='reset_lock', action="store_true",
    help='to drop the lock ')
def reset(reset_board=None, reset_lock=None):
    """
    drops the objects in the database
    required the board flag or lock flag to
    """
    # first try making the board
    if not (reset_lock or reset_board) and prompt_bool("Are you sure to drop them both?"):
        print("You didn't enter anything so creating both")
        reset_lock = True
        reset_board = True
    if try_connect_to_redis():
        if reset_board:
            if not board.drop():
                print('Found Error while dropping board')
            elif not board.create():
                print("Found Error while creating board")
            else:
                print('Board dropped successfully')
        if reset_lock:
            if not lock.drop():
                print('Found Error while dropping board')
            elif not lock.create():
                print("Found Error while creating board")
            else:
                print('Board dropped successfully')
    print("Command End")
