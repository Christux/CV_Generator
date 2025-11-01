from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import webbrowser
from generator import __version__


def parse_arguments(argv: list[str] | None):

    p = ArgumentParser(
        description="CV Generator",
        conflict_handler='resolve',
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    p.add_argument(
        '-v', '-V', '--version',
        action='version',
        help='show the version number',
        version=f'version is {__version__}'
    )

    p.add_argument('--open-browser', action='store_true',
                   help='open browser at startup')
    p.add_argument('--host', type=str, default='localhost',
                   help='host of the web server')
    p.add_argument('--port', type=int, default=5000,
                   help='port of the web server')
    p.add_argument('--debug', action='store_true', help='debug mode')

    return p.parse_args(argv)


def cli(argv: list[str] | None = None):

    try:
        args = parse_arguments(argv)

    except Exception as e:
        print('Sorry, something went wrong when parsing the given arguments')
        print(e)
        print(type(e))
