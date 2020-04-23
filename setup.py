"""
Author: Itamar Kannne
Main App
"""

if __name__ == '__main__':
    # first for all, monkey patch
    from eventlet import monkey_patch
    monkey_patch()

    import sys
    from painter.manager import cli
    from flask_script.commands import InvalidCommand

    try:
        cli()
    except InvalidCommand as err:
        # prints
        print(err, file=sys.stderr)
        sys.exit(1)
