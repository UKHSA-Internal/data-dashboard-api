import logging
import os

import requests

logger = logging.getLogger(__name__)

DEFAULT_REQUEST_TIMEOUT = 60


def _get_cdn_auth_key() -> str:
    try:
        cdn_auth_key = os.environ["CDN_AUTH_KEY"]
    except KeyError as error:
        raise KeyError("No CDN auth key specified") from error
    return f'"{cdn_auth_key}"'


def _hit_endpoint_for_json(url: str) -> dict:
    cdn_auth_key = _get_cdn_auth_key()
    response = requests.get(
        url=url,
        timeout=DEFAULT_REQUEST_TIMEOUT,
        headers={"x-cdn-auth": cdn_auth_key},
    )
    return response.json()


def _hit_endpoint_for_html(url: str) -> str:
    cdn_auth_key = _get_cdn_auth_key()
    response = requests.get(
        url=url,
        timeout=DEFAULT_REQUEST_TIMEOUT,
        headers={"Accept": "text/html", "x-cdn-auth": cdn_auth_key},
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


def crawl_public_api_themes_path():
    try:
        api_url = os.environ["PUBLIC_API_URL"]
    except KeyError as error:
        raise KeyError("No `PUBLIC_API_URL` provided") from error

    api_url = f"{api_url}/themes/"

    logger.info(f"Crawling from root URL {api_url}")
    crawl(api_url, crawled_urls=[])
