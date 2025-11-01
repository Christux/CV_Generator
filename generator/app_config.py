import os

class AppConfig():

    def __init__(self) -> None:
        self.debug = False
        self.dev_server = False
        self.module_path = ''
        self.config_file = 'config.yaml'
        self.dist_folder = 'dist'
        self.page_name = 'index.html'
        self.template_folder = 'templates'
        self.base_template = 'base.html'
        self.asset_folder = 'assets'
        self.server_host = 'localhost'
        self.server_port = 8080
        self.server_websocket_port = 8765

    @property
    def abs_dist_page_path(self) -> str:
        return os.path.join(self.dist_folder, self.page_name)

    @property
    def abs_template_folder_path(self) -> str:
        return os.path.join(self.template_folder)

    @property
    def abs_asset_folder_path(self) -> str:
        return os.path.join(self.asset_folder)

    @property
    def page_url(self) -> str:
        return f"http://{self.server_host}:{self.server_port}/{self.page_name}"
