import os
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader



def build_page() -> None:

    with open("config.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    print(data)

    env = Environment(loader=FileSystemLoader("templates"), autoescape=False)
    template = env.get_template("base.html")
    html_output = template.render(**data)

    os.makedirs("dist", exist_ok=True)
    with open("dist/index.html", "w", encoding="utf-8") as f:
        f.write(html_output)

    print("CV built successefully : dist/index.html")
