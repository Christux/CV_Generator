import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
from generator.app_config import AppConfig


class DeadLinkFinder():
    """A utility class to detect dead or broken links in generated HTML pages."""

    def __init__(self, app_config: AppConfig) -> None:
        """Initialize the dead link finder.

        Args:
            app_config (AppConfig): The application configuration instance.
        """
        self._app_config = app_config

    def extract_unique_links(self, html_text: str, base_url: str) -> list[str]:
        """Extract all unique, valid hyperlinks from an HTML document.

        This method parses the given HTML content and collects all unique
        hyperlinks that are not anchors, JavaScript calls, or mailto links.

        Args:
            html_text (str): The HTML content to analyze.
            base_url (str): The base URL used to resolve relative links.

        Returns:
            list[str]: A list of unique absolute URLs extracted from the HTML content.
        """
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

    def find_dead_links(self, html_text: str, base_url: str | None = None, timeout: int = 5, verify_ssl: bool = True) -> list[dict]:
        """Check all links in an HTML document for dead (unreachable) URLs.

        Each link is first tested using an HTTP HEAD request; if it fails or
        returns an error status code, a GET request is retried for confirmation.

        Args:
            html_text (str): The HTML document to analyze.
            base_url (str | None, optional): The base URL for resolving relative links. Defaults to None.
            timeout (int, optional): Timeout duration for each request, in seconds. Defaults to 5.
            verify_ssl (bool, optional): Whether to verify SSL certificates. Defaults to True.

        Returns:
            list[dict]: A list of dictionaries describing dead links, where each dictionary contains:
                - "url" (str): The problematic link.
                - "status" (int | None): The HTTP status code or None if unreachable.
                - "error" (str): The error message or reason.
        """
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
                        url, allow_redirects=True, timeout=timeout,
                        verify=verify_ssl, headers=headers)

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

    def find_dead_links_in_dist(self) -> None:
        """Find and display dead links in the generated distribution HTML page.

        Reads the main HTML file from the distribution folder, scans for dead
        links, and prints each broken URL with its corresponding error message.
        """
        with open(file=self._app_config.abs_dist_page_path, mode="r", encoding="utf-8") as file:
            html = file.read()

        dead_links = self.find_dead_links(html_text=html, verify_ssl=True)

        for link in dead_links:
            print(f"❌ {link['url']} → {link['error']}")
