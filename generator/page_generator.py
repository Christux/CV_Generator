import os
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader
from generator.app_config import AppConfig


class PageGenerator():

    def __init__(self, app_config: AppConfig) -> None:
        self.app_config = app_config

    def build_page(self) -> None:

        with open(file=self.app_config.config_file, mode="r", encoding="utf-8") as file:
            data = yaml.safe_load(stream=file)

        if self.app_config.debug:
            print(data)

        env = Environment(
            loader=FileSystemLoader(searchpath=self.app_config.abs_template_folder_path),
            autoescape=False)

        template = env.get_template(name=self.app_config.base_template)

        html_output = template.render(**data)

        if self.app_config.dev_server:
            reload_script = f"""
<script>
const ws = new WebSocket("ws://{self.app_config.server_host}:{self.app_config.server_websocket_port}");
ws.onmessage = (e) => {{ if (e.data === "reload") location.reload(); }};
</script>
"""
            html_output = html_output.replace("</body>", reload_script + "\n</body>")

        os.makedirs(self.app_config.dist_folder, exist_ok=True)

        with open(file=self.app_config.abs_dist_page_path, mode="w", encoding="utf-8") as file:
            file.write(html_output)

        print(f"CV built successefully : {self.app_config.abs_dist_page_path}")
