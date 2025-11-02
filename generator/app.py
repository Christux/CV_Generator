from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
import webbrowser
from generator import __version__
from generator.app_config import AppConfig
from generator.dev_server import DevServer
from generator.ftp_uploader import FTPUploader
from generator.page_generator import PageGenerator


class App():

    def __init__(self, app_config: AppConfig) -> None:
        self._app_config = app_config

    def _parse_arguments(self, argv: list[str] | None) -> Namespace:

        parser = ArgumentParser(
            description="CV Generator",
            conflict_handler='resolve',
            formatter_class=ArgumentDefaultsHelpFormatter
        )

        parser.add_argument(
            '-v', '-V', '--version',
            action='version',
            help='show the version number',
            version=f'version is {__version__}'
        )

        group = parser.add_mutually_exclusive_group(required=True)

        group.add_argument('--build', action='store_true',
                           help='build the page')

        group.add_argument('--dev-server', action='store_true',
                           help='enable developpement server')
        
        group.add_argument('--upload', action='store_true',
                           help='upload to web server with FTP')

        parser.add_argument('--open-browser', action='store_true',
                            help='open browser at startup')

        parser.add_argument('--host', type=str, default='localhost',
                            help='host of the web server')

        parser.add_argument('--port', type=int, default=5000,
                            help='port of the web server')

        parser.add_argument('--debug', action='store_true', help='debug mode')

        return parser.parse_args(argv)

    def start_cli(self, argv: list[str] | None = None) -> None:

        args = Namespace()

        try:
            args = self._parse_arguments(argv)

            if args.debug:
                print("Debuggin mode")
                self._app_config.debug = True

            if args.dev_server:
                print("Developpement server enabled")
                self._app_config.dev_server = True

        except Exception as e:
            print('Sorry, something went wrong when parsing the given arguments')
            print(e)
            print(type(e))

        try:

            if args.build:
                print('Build the page...')
                pg = PageGenerator(app_config=self._app_config)
                pg.build_page()

            if args.dev_server:
                print('Serving the page in dev mode...')
                pg = PageGenerator(app_config=self._app_config)
                pg.build_page()
                server = DevServer(
                    app_config=self._app_config, page_generator=pg)

                if args.open_browser:
                    webbrowser.open(self._app_config.page_url)

                server.serve()

            if args.upload:
                print('Upload to server')
                uploader = FTPUploader(app_config=self._app_config)
                uploader.upload()

        except Exception as e:
            print('Sorry, something went wrong !')
            print(e)
            print(type(e))
