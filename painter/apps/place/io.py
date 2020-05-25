import json
from datetime import datetime
from typing import Any, Dict, Optional
from painter.backends.extensions import cache
from flask_login import current_user
from typing import Callable
from painter.backends import lock, board
from painter.backends.extensions import storage_sql
from painter.backends.skio import (
    sio, PAINT_NAMESPACE,
    socket_io_authenticated_only_connection,
    socket_io_authenticated_only_event,
)
from painter.others.constants import COLOR_COOLDOWN
from functools import wraps


def task_set_board(x: int, y: int, color: int) -> None:
    """
    :param x: valid x coordinate
    :param y: valid y coordinate
    :param color: color of the pixel
    :return: nothing
    sets a pixel on the screen
    -- sets the pixel in the redis server
    -- broadcast to all watchers that the pixel has changed
    """
    board.set_at(x, y, color)
    sio.emit('set-board', (x, y, color), namespace=PAINT_NAMESPACE)


@sio.on('connect', PAINT_NAMESPACE)
@socket_io_authenticated_only_connection
def connect():
    """
    :return: suppose to do thing, just reject any connection from users
    """
    pass


def dispatch_lock(lock_val: Optional[bool]) -> None:
    """
    :return: dispatch a lock value
    """
    return not lock_val if lock_val is not None else None


@sio.on('get-start', PAINT_NAMESPACE)
@socket_io_authenticated_only_event
def get_start_data() -> Optional[Dict[str, Any]]:
    """
    :return: the start data of the user {
    board in pixels:bytes,
    time: the next time the user can update the board,
    lock: if the board is locked
    }
    """
    requested_keys = {
        'locked': dispatch_lock(lock.is_open()),
        'board': board.get_board(),
        'time': str(current_user.next_time)
    }
    if any(key is None for key in requested_keys):
        return None
    return requested_keys


def limit_user_calls(timeout_between_request: int,
                     response_result: Callable,
                     wrapper_cache_key: Optional[str] = None,
                     ) -> Callable:
    """
    :param timeout_between_request: the time to cache
    :param wrapper_cache_key: key prefix for user
    :param response_result: the response sent when fail to capture
    :return: the function result
    """

    def wrapper(route: Callable, _cache_prefix: Optional[str]) -> Callable:
        """
        :param route: io wrapper
        :param _cache_prefix: the cached key format
        :return: the wrapped function
        a wrapped function to prevent user exploits of timing
        using the cache module prevents the user to access the function
        """
        _cache_prefix = _cache_prefix if _cache_prefix is not None else route.__name__ + ':%d'

        # first default key prefix is the function name:id
        @wraps(route)
        def wrapped(*args, **kwargs):
            # first cache
            cached_key = _cache_prefix % current_user.id
            if cache.get(cached_key) is None:
                # set
                cache.set(cached_key, True, timeout=timeout_between_request)
                result = route(*args, **kwargs)
                # delete cached key
                cache.delete(cached_key)
                return result
            else:
                return response_result

        return wrapped

    return lambda func: wrapper(func, wrapper_cache_key)


@sio.on('set-board', PAINT_NAMESPACE)
@socket_io_authenticated_only_event
@limit_user_calls(
    7, None
)
def set_board(params: Any) -> str:
    """
    :param params: params given to the Dictionary
    :return: string represent the next time the user can update the canvas,
    or undefined if couldn't update the screen
    """
    # try
    # first set user in cache
    # give 15 seconds cooldown between each request to prevent re-auto clicking
    try:
        # get current_time in utc
        current_time = datetime.utcnow()
        # if the still cant update the board
        if current_user.next_time > current_time:
            return json.dumps({'code': 'time', 'status': str(current_user.next_time)})
        # if the board is locked
        if not lock.is_open():
            return json.dumps({'code': 'lock', 'status': 'true'})
        # validating parameter
        if 'x' not in params or (not isinstance(params['x'], int)) or not (0 <= params['x'] < 1000):
            return 'undefined'
        if 'y' not in params or (not isinstance(params['y'], int)) or not (0 <= params['y'] < 1000):
            return 'undefined'
        if 'color' not in params or (not isinstance(params['color'], int)) or not (0 <= params['color'] < 16):
            return 'undefined'
        # the data is valid, so emit the response
        # update next time
        next_time = current_time + COLOR_COOLDOWN
        current_user.next_time = next_time
        # update current_user in the SQL Database
        storage_sql.session.add(current_user)
        storage_sql.session.commit()
        # get data
        x, y, clr = int(params['x']), int(params['y']), int(params['color'])
        # start background task
        sio.start_background_task(task_set_board, x=x, y=y, color=clr)
        #  board.set_at(x, y, color)
        return json.dumps({'code': 'time', 'status': str(next_time)})
    # exception handling
    except Exception as e:
        print(e)
        return 'undefined'
