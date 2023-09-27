import logging
import os

import requests

logger = logging.getLogger(__name__)
DEFAULT_REQUEST_TIMEOUT = 60


def _get_api_key() -> str:
    api_key = os.environ.get("API_KEY")
    return f'"{api_key}"'


def _hit_endpoint_for_json(url: str) -> dict:
    api_key = _get_api_key()
    response = requests.get(
        url=url,
        timeout=DEFAULT_REQUEST_TIMEOUT,
        headers={"Accept": "application/json", "x-cdn-auth": api_key},
    )
    return response.json()


def _hit_endpoint_for_html(url: str) -> str:
    api_key = _get_api_key()
    response = requests.get(
        url=url,
        timeout=DEFAULT_REQUEST_TIMEOUT,
        headers={"Accept": "text/html", "x-cdn-auth": api_key},
    )
    return response.content


def crawl(url: str, crawled_urls: list[str]) -> None:
    logger.info(f" Calling {url}")
    _hit_endpoint_for_html(url=url)
    api_level: dict = _hit_endpoint_for_json(url=url)

    targets: list[str] = get_targets_from_api_response(api_level)

    for target in targets:
        if target not in crawled_urls:
            crawled_urls.append(target)
            logger.info(f"{len(crawled_urls)} URLs crawled")
            crawl(url=target, crawled_urls=crawled_urls)

    return crawled_urls


def get_targets_from_api_response(api_level: dict) -> list[str]:
    targets = []
    for links in api_level:
        if isinstance(links, dict):
            for key, value in links.items():
                if _is_url(value=value):
                    targets.append(value)

    return targets


def _is_url(value: str) -> bool:
    return "http" in value


def crawl_public_api():
    api_url = os.environ.get("PUBLIC_API_URL")

    if api_url is None:
        raise ValueError("No `PUBLIC_API_URL` provided")

    api_url = f"{api_url}/themes/"

    logger.info(f"Crawling from root URL {api_url}")
    crawl(api_url, crawled_urls=[])
