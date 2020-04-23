"""
Author: Itamar Kannne
Main App
"""

if __name__ == '__main__':
    # first for all, monkey patch
    from eventlet import monkey_patch
    monkey_patch()
    # client
    from painter.manager import cli
    cli()

