from datetime import datetime
import os
import shutil
from typing import Any
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader
from generator.app_config import AppConfig


class PageGenerator():

    def __init__(self, app_config: AppConfig) -> None:
        self.app_config = app_config

    def convert_markdown(self, text: Any) -> Any:
        if isinstance(text, str):
            return markdown.markdown(text)
        if isinstance(text, list):
            return [self.convert_markdown(x) for x in text]
        if isinstance(text, dict):
            return {k: self.convert_markdown(v) for k, v in text.items()}
        return text

    def render_template(self, data: Any) -> str:
        env = Environment(
            loader=FileSystemLoader(searchpath=self.app_config.abs_template_folder_path),
            autoescape=False)

        template = env.get_template(name=self.app_config.base_template)

        return template.render(**data)

    def add_hot_reload_script(self, html: str) -> str:
        if self.app_config.dev_server:
            reload_script = f"""
                <script>
                const ws = new WebSocket("ws://{self.app_config.server_host}:{self.app_config.server_websocket_port}");
                ws.onmessage = (e) => {{ if (e.data === "reload") location.reload(); }};
                </script>
                """
            return html.replace("</body>", reload_script + "\n</body>")

        return html
    
    def build_assets(self, build_id: str, assets_conf: Any | None = None) -> None:

        css_src = os.path.join(self.app_config.asset_folder, "css")
        js_src = os.path.join(self.app_config.asset_folder, "js")
        css_out = os.path.join(self.app_config.dist_folder, "css", f"style.{build_id}.css")
        js_out = os.path.join(self.app_config.dist_folder, "js", f"main.{build_id}.js")

        os.makedirs(os.path.join(self.app_config.dist_folder, "css"), exist_ok=True)
        os.makedirs(os.path.join(self.app_config.dist_folder, "js"), exist_ok=True)

        css_files = assets_conf.get("css") if assets_conf else None
        js_files = assets_conf.get("js") if assets_conf else None

        if os.path.isdir(css_src):
            self.concat_files(css_src, css_files, [".css"], css_out)
        if os.path.isdir(js_src):
            self.concat_files(js_src, js_files, [".js"], js_out)

        self.copy_extra_assets(self.app_config.asset_folder, self.app_config.dist_folder)

    def concat_files(self, src_dir, filenames, extensions, out_file):

        os.makedirs(os.path.dirname(out_file), exist_ok=True)

        with open(out_file, "w", encoding="utf-8") as outfile:
            if filenames:
                for fname in filenames:
                    src_path = os.path.join(src_dir, fname)
                    if not os.path.isfile(src_path):
                        print(f"Missing file : {fname}")
                        continue
                    with open(src_path, "r", encoding="utf-8") as infile:
                        outfile.write(f"/* {fname} */\n")
                        outfile.write(infile.read().strip() + "\n\n")
                        print(f"Added to {os.path.basename(out_file)} : {fname}")
            else:
                for fname in sorted(os.listdir(src_dir)):
                    if os.path.splitext(fname)[1] in extensions:
                        src_path = os.path.join(src_dir, fname)
                        with open(src_path, "r", encoding="utf-8") as infile:
                            outfile.write(f"/* {fname} */\n")
                            outfile.write(infile.read().strip() + "\n\n")
                            print(f"Added to {os.path.basename(out_file)} : {fname}")


    def copy_extra_assets(self, src_dir, dst_dir):

        for root, _, files in os.walk(src_dir):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext not in [".css", ".js"]:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, src_dir)
                    dst_path = os.path.join(dst_dir, rel_path)
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)



    def build_page(self) -> None:

        build_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        with open(file=self.app_config.config_file, mode="r", encoding="utf-8") as file:
            data = yaml.safe_load(stream=file)

        if self.app_config.debug:
            print(data)

        #data = self.convert_markdown(text=data)

        # if self.app_config.debug:
        #     print(data)

        assets_conf = data.get("assets")
        self.build_assets(build_date, assets_conf)

        html_output = self.render_template(data=data)

        html_output = self.add_hot_reload_script(html_output)

        os.makedirs(self.app_config.dist_folder, exist_ok=True)

        with open(file=self.app_config.abs_dist_page_path, mode="w", encoding="utf-8") as file:
            file.write(html_output)

        print(f"CV built successefully : {self.app_config.abs_dist_page_path}")
