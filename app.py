from sbir import create_app

__author__ = 'dwcaraway'

app = create_app()

if __name__ == '__main__':
    import logging
    import sys
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    app.run()

