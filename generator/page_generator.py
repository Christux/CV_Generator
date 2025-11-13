from datetime import datetime
import glob
import os
import re
import shutil
from typing import Any
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader, Template
from generator.app_config import AppConfig
from generator.jinja_filters import first_date_filter


class PageGenerator():
    """Page generator responsible for building the static CV page and related assets."""

    def __init__(self, app_config: AppConfig) -> None:
        """Initialize the page generator.

        Args:
            app_config (AppConfig): The application configuration instance.
        """
        self._app_config = app_config

    def _convert_markdown(self, data: Any, key: str | None = None) -> Any:
        """Recursively convert Markdown content to HTML.

        Args:
            data (Any): Input data (dict, list, or string).
            key (str | None): Current key name in traversal (used to detect 'content' fields).

        Returns:
            Any: Data with Markdown strings converted to HTML.
        """
        if key == 'content' and isinstance(data, str):
            if self._app_config.debug:
                print(data)
            return markdown.markdown(data)

        if isinstance(data, list):
            return [self._convert_markdown(x) for x in data]

        if isinstance(data, dict):
            return {k: self._convert_markdown(v, k) for k, v in data.items()}

        return data

    def _transform_braces_to_span(self, text: str) -> str:
        """Transform brace-style markup into <span> tags.

        Example:
            Input: "{highlight:Important}"
            Output: '<span class="highlight">Important</span>'

        Args:
            text (str): Text containing brace-style markup.

        Returns:
            str: Text with braces transformed into HTML span tags.
        """
        pattern = r"\{([\w-]+):(.+?)\}"
        return re.sub(pattern, r'<span class="\1">\2</span>', text, flags=re.DOTALL)

    def _apply_style_tags(self, data: Any) -> Any:
        """Apply span-style transformations recursively across data.

        Args:
            data (Any): Input data (string, list, or dict).

        Returns:
            Any: Data with style tags applied.
        """
        if isinstance(data, str):
            if self._app_config.debug:
                print(data)
            return self._transform_braces_to_span(text=data)

        if isinstance(data, list):
            return [self._apply_style_tags(x) for x in data]

        if isinstance(data, dict):
            if self._app_config.debug:
                print(data)
            return {k: self._apply_style_tags(v) for k, v in data.items()}

        return data

    def _render_template(self, data: Any) -> str:
        """Render the main HTML page using Jinja2.

        Args:
            data (Any): Data dictionary to render into the template.

        Returns:
            str: Rendered HTML content.
        """
        env = Environment(
            loader=FileSystemLoader(
                searchpath=self._app_config.abs_template_folder_path),
            autoescape=False)
        env.filters['first_date'] = first_date_filter
        template = env.get_template(name=self._app_config.base_template)
        return template.render(**data)

    def _render_site_map(self, data: Any) -> str:
        """Render the sitemap XML template.

        Args:
            data (Any): Data dictionary for the sitemap template.

        Returns:
            str: Rendered sitemap XML.
        """
        with open(file=self._app_config.abs_sitemap, mode="r", encoding="utf-8") as f:
            template = Template(f.read())
        return template.render(**data)

    def _add_hot_reload_script(self, html: str) -> str:
        """Inject a live-reload WebSocket script for development mode.

        Args:
            html (str): The generated HTML content.

        Returns:
            str: HTML with reload script appended before </body>.
        """
        if self._app_config.dev_server:
            reload_script = f"""
                <script>
                const ws = new WebSocket("ws://{self._app_config.server_host}:{self._app_config.server_websocket_port}");
                ws.onmessage = (e) => {{ if (e.data === "reload") location.reload(); }};
                </script>
                """
            return html.replace("</body>", reload_script + "\n</body>")

        return html

    def _build_assets(self, build_id: str, assets_conf: Any | None = None) -> None:
        """Build and concatenate CSS and JS assets for the site.

        Args:
            build_id (str): Unique build identifier appended to filenames.
            assets_conf (Any | None): Optional configuration specifying assets to include.
        """
        css_src = os.path.join(self._app_config.asset_folder, "css")
        js_src = os.path.join(self._app_config.asset_folder, "js")
        css_out = os.path.join(self._app_config.dist_folder, "css",
                               f"{self._app_config.css_file_name}.{build_id}.css")
        js_out = os.path.join(self._app_config.dist_folder, "js",
                              f"{self._app_config.js_file_name}.{build_id}.js")

        os.makedirs(os.path.join(
            self._app_config.dist_folder, "css"), exist_ok=True)
        os.makedirs(os.path.join(
            self._app_config.dist_folder, "js"), exist_ok=True)

        self._cleanup_old_assets()

        css_files = assets_conf.get("css") if assets_conf else None
        js_files = assets_conf.get("js") if assets_conf else None

        if os.path.isdir(css_src):
            self._concat_files(css_src, css_files, [".css"], css_out)
        if os.path.isdir(js_src):
            self._concat_files(js_src, js_files, [".js"], js_out)

        self._copy_extra_assets(
            self._app_config.asset_folder, self._app_config.dist_folder)

    def _cleanup_old_assets(self) -> None:
        """Remove old CSS and JS files from the distribution directory."""
        css_pattern = os.path.join(
            self._app_config.dist_folder, "css", "*.css")
        js_pattern = os.path.join(self._app_config.dist_folder, "js", "*.js")
        removed = []

        for pattern in [css_pattern, js_pattern]:
            for file_path in glob.glob(pattern):
                try:
                    os.remove(file_path)
                    removed.append(os.path.basename(file_path))
                except Exception as e:
                    print(f"Unable to remove {file_path}: {e}")

        if removed:
            print(f"Cleanup : files erased {', '.join(removed)}")
        else:
            print("No, file to erase")

    def _concat_files(self, src_dir: str, filenames: list[str] | None,
                      extensions: list[str], out_file: str) -> None:
        """Concatenate multiple source files into a single output file.

        Args:
            src_dir (str): Source directory containing asset files.
            filenames (list[str] | None): Specific filenames to include. If None, includes all matching extensions.
            extensions (list[str]): File extensions to include (e.g. [".css"]).
            out_file (str): Path of the output file.
        """
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
                        print(
                            f"Added to {os.path.basename(out_file)} : {fname}")
            else:
                for fname in sorted(os.listdir(src_dir)):
                    if os.path.splitext(fname)[1] in extensions:
                        src_path = os.path.join(src_dir, fname)
                        with open(src_path, "r", encoding="utf-8") as infile:
                            outfile.write(f"/* {fname} */\n")
                            outfile.write(infile.read().strip() + "\n\n")
                            print(
                                f"Added to {os.path.basename(out_file)} : {fname}")

    def _copy_extra_assets(self, src_dir: str, dst_dir: str) -> None:
        """Copy non-CSS/JS assets (e.g. images, fonts) to the distribution folder.

        Args:
            src_dir (str): Source assets directory.
            dst_dir (str): Destination directory for copied assets.
        """
        for root, _, files in os.walk(src_dir):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext not in [".css", ".js"]:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, src_dir)
                    dst_path = os.path.join(dst_dir, rel_path)
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)

    def _load_config(self) -> Any:
        """Load YAML configuration from the config file.

        Returns:
            Any: Parsed YAML configuration dictionary.
        """
        with open(file=self._app_config.config_file, mode="r", encoding="utf-8") as file:
            config = yaml.safe_load(stream=file)
        return config

    def _load_data(self) -> Any:
        """Load YAML data from the data file.

        Returns:
            Any: Parsed YAML data dictionary.
        """
        with open(file=self._app_config.data_file, mode="r", encoding="utf-8") as file:
            data = yaml.safe_load(stream=file)
        return data

    def _save_page(self, html: str) -> None:
        """Save the generated HTML page to the distribution folder.

        Args:
            html (str): HTML content to save.
        """
        with open(file=self._app_config.abs_dist_page_path, mode="w", encoding="utf-8") as file:
            file.write(html)

    def _save_sitemap(self, sitemap: str) -> None:
        """Save the rendered sitemap to the distribution folder.

        Args:
            sitemap (str): Sitemap content to save.
        """
        with open(file=self._app_config.abs_dist_sitemap, mode="w", encoding="utf-8") as file:
            file.write(sitemap)

    def build_page(self) -> None:
        """Build the entire CV page and related assets.

        This method:
        - Loads configuration and data files.
        - Converts Markdown and applies style transformations.
        - Builds CSS and JS assets.
        - Renders HTML and sitemap templates.
        - Saves the final files to the distribution folder.
        """
        config = self._load_config()
        data = self._load_data()

        build_id = datetime.now().strftime("%Y%m%d%H%M%S")
        build_year = datetime.now().year
        build_date = datetime.now().strftime("%Y-%m-%d")

        data['build_id'] = build_id
        data['build_date'] = build_date
        data['build_year'] = build_year

        data['html'] = {
            'css_file_name': self._app_config.css_file_name,
            'js_file_name': self._app_config.js_file_name
        }

        if self._app_config.debug:
            print(data)

        data = self._convert_markdown(data=data)
        data = self._apply_style_tags(data=data)

        if self._app_config.debug:
            print(data)

        os.makedirs(self._app_config.dist_folder, exist_ok=True)

        assets_conf = config.get("assets")

        self._build_assets(build_id, assets_conf)

        html_output = self._render_template(data=data)
        html_output = self._add_hot_reload_script(html_output)
        self._save_page(html=html_output)

        sitemap = self._render_site_map(data=data)
        self._save_sitemap(sitemap=sitemap)

        print(
            f"CV built successfully : {self._app_config.abs_dist_page_path}")
