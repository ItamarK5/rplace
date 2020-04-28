import time
from typing import Any, FrozenSet, Dict, Optional, Union, List

from flask_script import Command, Option
from redis.exceptions import (
    RedisError, AuthenticationWrongNumberOfArgsError, AuthenticationError,
    TimeoutError as RedisTimeout,
    ConnectionError as RedisConnectionError
)

from painter.backends.extensions import redis, storage_sql
from ..others.constants import (
    DURATION_OPTION_FLAG,
    PRINT_OPTION_FLAG,
    FLAG_SERVICES_OPTIONS,
    SERVICE_RESULTS_FORMAT
)


def has_service_option(flags: Union[bool, List[str]], *options) -> bool:
    """
    :param flags: the service flags passed
    :param options: list of options for a option for check-services
    :return: if the option service enabled
    """
    if not isinstance(flags, list):
        return flags
    # other option flag is empty
    elif not flags:
        return True
    for option in options:
        if option in flags:
            return True
    return False


def parse_service_options(flags: Union[bool, List[str]]) -> FrozenSet[str]:
    """
    :param flags: the raw services flags options the user gave
    :return: the flags as set of values the all the values there represent setted flags
    """
    return frozenset(
        option
        for option in FLAG_SERVICES_OPTIONS
        if has_service_option(flags, FLAG_SERVICES_OPTIONS[option])
    )


def check_service_flag(service_flag: Optional[bool], all_flag: bool) -> bool:
    """
    :param service_flag: if entered the flag of the service
    :param all_flag: if the check all flag passed
    :return the value of the all flag if the user didnt passed an service flag but
    if he d'idnt passed its the value that dont match to all flag
    """
    return all_flag if service_flag is None else service_flag ^ all_flag


def check_redis_service(option_flags: FrozenSet[str]) -> Dict[str, Any]:
    """
    :param option_flags: option flags to check
    :return: redis-service response data
    --name
    --status
    --time taken to execute
    """
    result = False
    duration = 'None'
    try:
        if DURATION_OPTION_FLAG in option_flags:
            current_time = time.time()
            redis.ping()
            duration = time.time() - current_time
        else:
            redis.ping()
        if PRINT_OPTION_FLAG in option_flags:
            print('Successfully ping to redis')
        result = True
    except AuthenticationWrongNumberOfArgsError:
        if PRINT_OPTION_FLAG in option_flags:
            print('Cannot Auth to redis, check your password again')
    except AuthenticationError:
        if PRINT_OPTION_FLAG in option_flags:
            print('Cannot Authenticate to server')
    except RedisTimeout:
        if PRINT_OPTION_FLAG in option_flags:
            print('redis timeout, cannot connect to redis server')
    except RedisConnectionError:
        if PRINT_OPTION_FLAG in option_flags:
            print('Connection closed by server, it must be because')
    except RedisError as e:
        if PRINT_OPTION_FLAG in option_flags:
            print("Unknown Error")
            print(repr(e))
    finally:
        return {
            'service_name': 'redis',
            'result': 'Connected' if result else 'Error',
            'duration': duration if DURATION_OPTION_FLAG else 'None'
        }


def check_sql_service(option_flags: FrozenSet[str]) -> Dict[str, Any]:
    """
    :param option_flags: option flags to check
    :return: sql database-service response data
    --name
    --status
    --time taken to execute
    """
    result = False
    duration = 'None'
    try:
        # connection
        if DURATION_OPTION_FLAG in option_flags:
            current_time = time.time()
            storage_sql.engine.connect()
            duration = time.time() - current_time
        else:
            storage_sql.engine.connect()
        if PRINT_OPTION_FLAG in option_flags:
            print('Successfully connected to sql')
        result = True
    except Exception as e:
        print("Fail to connect to SQL Alchemy")
        raise e
    finally:
        return {
            'service_name': 'SQL',
            'result': 'Connected' if result else 'Error',
            'duration': duration if DURATION_OPTION_FLAG else 'None'
        }


def check_services(all=False, rds=None, sql=None, options=None):
    """
   checks if the service the app needs to run are active
   there are currently two:
   1) redis server
   2) sql
    """
    # if in the future I should add other flags
    # check if all of them are None
    options = parse_service_options(options)
    # if all of them are None, check them all
    rds = check_service_flag(rds, all)
    results = []
    # redis check
    if rds:
        # time check
        print('checks if can connect to redis')
        # try with redis
        results.append(check_redis_service(options))
    # check sqlite
    sql = check_service_flag(sql, all)
    # redis check
    if sql:
        # time check
        print('checks if can connect to sql')
        # try with redis
        results.append(check_sql_service(options))
    # print all
    enabled_contexts = tuple(filter(
        lambda option_context: option_context.is_option_enabled(options),
        SERVICE_RESULTS_FORMAT
    ))
    # get result format for contexts
    result_format = '|'.join(context.string_format for context in enabled_contexts)
    print(result_format.format(*[context.title for context in enabled_contexts]))
    for result in results:
        print(result_format.format(*[str(result[context.key]) for context in enabled_contexts]))


check_services_command = Command(check_services)
check_services_command.add_option(Option(
    '--r', '-redis', dest='rds', action='store_true', help='to check update with redis'
))
check_services_command.add_option(Option(
    '--s', '-sql', dest='sql', action='store_true', help='to check update with sqlalchemy'
))
check_services_command.add_option(Option(
    '--a', '-all', dest='all', action='store_true', help='to check update with all'
))
check_services_command.add_option(Option(
    '--o', '-options', nargs='*', dest='options',
    help='special options for the command: t for display the time it takes to end and'
         'p to print messages'
))
