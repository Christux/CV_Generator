import os

class AppConfig():
    """Application configuration handler.

    This class defines and manages configuration settings for a web application,
    including file paths, server configuration, and resource naming conventions.
    """

    def __init__(self) -> None:
        """Initialize default configuration values.

        Sets up default parameters for file names, directories, and server properties.
        """
        self.debug = False
        self.dev_server = False
        self.config_file = 'config.yaml'
        self.data_file = 'data.yaml'
        self.credential_file = 'credentials.yaml'
        self.dist_folder = 'dist'
        self.page_name = 'index.html'
        self.sitemap = 'sitemap.xml'
        self.template_folder = 'templates'
        self.base_template = 'base.html'
        self.asset_folder = 'assets'
        self.server_host = 'localhost'
        self.server_port = 8080
        self.server_websocket_port = 8765
        self.css_file_name = 'style'
        self.js_file_name = 'script'

    @property
    def abs_dist_page_path(self) -> str:
        """Get the absolute path to the distribution page file.

        Returns:
            str: The absolute path of the main distribution HTML page.
        """
        return os.path.join(self.dist_folder, self.page_name)

    @property
    def abs_sitemap(self) -> str:
        """Get the absolute path to the sitemap in the template folder.

        Returns:
            str: The absolute path to the sitemap file located in the template folder.
        """
        return os.path.join(self.template_folder, self.sitemap)

    @property
    def abs_dist_sitemap(self) -> str:
        """Get the absolute path to the sitemap in the distribution folder.

        Returns:
            str: The absolute path to the sitemap file located in the distribution folder.
        """
        return os.path.join(self.dist_folder, self.sitemap)

    @property
    def abs_template_folder_path(self) -> str:
        """Get the absolute path to the template folder.

        Returns:
            str: The absolute path of the template folder.
        """
        return os.path.join(self.template_folder)

    @property
    def abs_asset_folder_path(self) -> str:
        """Get the absolute path to the asset folder.

        Returns:
            str: The absolute path of the asset folder.
        """
        return os.path.join(self.asset_folder)

    @property
    def page_url(self) -> str:
        """Get the full URL of the main page served by the web server.

        Returns:
            str: The complete URL of the main web page, including host and port.
        """
        return f"http://{self.server_host}:{self.server_port}/{self.page_name}"
