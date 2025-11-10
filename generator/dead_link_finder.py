import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
from generator.app_config import AppConfig


class DeadLinkFinder():

    def __init__(self, app_config: AppConfig) -> None:
        self._app_config = app_config

    def extract_unique_links(self, html_text, base_url) -> list[str]:
        soup = BeautifulSoup(html_text, "html.parser")
        seen = set()
        unique_links = []

        for tag in soup.find_all("a", href=True):
            href = tag["href"].strip()
            
            if not href or href.startswith("#") or href.lower().startswith(("mailto:", "javascript:")):
                continue

            url = urljoin(base_url, href) if base_url else href

            if url not in seen:
                seen.add(url)
                unique_links.append(url)

        return unique_links

    def find_dead_links(self, html_text: str, base_url=None, timeout=5, verify_ssl=True):

        dead_links = []

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection": "keep-alive",
        }

        for url in self.extract_unique_links(html_text=html_text, base_url=base_url):

            if self._app_config.debug:
                print(f'Test link: {url}')

            try:
                response = requests.head(
                    url, allow_redirects=True, timeout=timeout, verify=verify_ssl, headers=headers)

                if self._app_config.debug:
                    if response.status_code == 200:
                        print('success')
                    else:
                        print('error')

                if response.status_code >= 400:
                    if self._app_config.debug:
                        print('retry')
                    time.sleep(0.5)
                    response = requests.get(
                        url, allow_redirects=True, timeout=timeout, verify=verify_ssl, headers=headers)

                if response.status_code >= 400:
                    if self._app_config.debug:
                        if response.status_code == 200:
                            print('success')
                        else:
                            print('error')

                    dead_links.append({
                        "url": url,
                        "status": response.status_code,
                        "error": response.reason
                    })

            except requests.RequestException as e:
                dead_links.append({
                    "url": url,
                    "status": None,
                    "error": str(e)
                })

            time.sleep(0.5)

        return dead_links

    def find_dead_links_in_dist(self):

        with open(file=self._app_config.abs_dist_page_path, mode="r", encoding="utf-8") as file:
            html = file.read()

        dead_links = self.find_dead_links(html_text=html, verify_ssl=True)

        for link in dead_links:
            print(f"❌ {link['url']} → {link['error']}")
