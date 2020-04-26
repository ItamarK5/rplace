"""
Author: Itamar Kannne
Main App
"""

if __name__ == '__main__':
    from eventlet import monkey_patch
    monkey_patch()
    # import staff
    import sys
    from flask_script.commands import InvalidCommand
    from painter.manager import manager
    # then run manager
    try:
        manager.run()
    except InvalidCommand as err:
        # prints
        print(err, file=sys.stderr)
        sys.exit(1)
