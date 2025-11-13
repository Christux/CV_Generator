

from generator.app_config import AppConfig
from generator.dead_link_finder import DeadLinkFinder


def test_dead_link_finder():

    html = """
<html><body>
  <a href="https://www.google.com/">Google</a>
  <a href="https://example.com/404page">Lien cassé</a>
  <a href="/relative/path">Relatif</a>
  <a href="#ancre">Ancre</a>
</body></html>
"""

    app_config = AppConfig()

    dlf = DeadLinkFinder(app_config=app_config)

    dead_links = dlf.find_dead_links(html_text=html)

    assert len(dead_links) == 2
