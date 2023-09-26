import logging

import requests

logger = logging.getLogger(__name__)


def _hit_endpoint_for_json(url: str) -> dict:
    response = requests.get(url)
    return response.json()


def _hit_endpoint_for_html(url: str) -> str:
    response = requests.get(url, headers={"Accept": "text/html"})
    return response.content


def crawl(url: str, crawled_urls: list[str]) -> None:
    print(f" Calling {url}")
    _hit_endpoint_for_html(url=url)
    api_level: dict = _hit_endpoint_for_json(url=url)

    targets: list[str] = get_targets_from_api_response(api_level)

    for target in targets:
        if target not in crawled_urls:
            crawled_urls.append(target)
            print(f"---------  {len(crawled_urls)} URLs crawled ---------")
            crawl(url=target, crawled_urls=crawled_urls)

    return crawled_urls


def get_targets_from_api_response(api_level: dict) -> list[str]:
    targets = []
    for links in api_level:
        if isinstance(links, dict):
            for key, value in links.items():
                if "http" in value:
                    targets.append(value)

    return targets


def crawl_public_api():
    import os

    api_url = os.environ.get("PUBLIC_API_URL")

    if api_url is None:
        raise ValueError("No `PUBLIC_API_URL` can't crawl public API right now")

    print(f"Crawling from root URL {api_url}")
    crawl(api_url, crawled_urls=[])
