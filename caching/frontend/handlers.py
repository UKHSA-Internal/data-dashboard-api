import os

from caching.frontend.crawler import FrontEndCrawler
from caching.public_api.handlers import get_cdn_auth_key


class FrontEndURLNotProvidedError(Exception): ...


def _get_frontend_base_url() -> str:
    """Returns the value of the "FRONTEND_URL" environment variable

    Returns:
        The value of the "FRONTEND_URL"

    Raises:
        `FrontEndURLNotProvidedError`: If the "FRONTEND_URL"
            environment variable has not been set

    """
    try:
        return os.environ["FRONTEND_URL"]
    except KeyError as error:
        raise FrontEndURLNotProvidedError from error


def crawl_front_end() -> None:
    """Traverse all relevant pages on the frontend

    Returns:
        None

    Raises:
        `FrontEndURLNotProvidedError`: If the "FRONTEND_URL"
            environment variable has not been set
        `CDNAuthKeyNotProvidedError`: If the "CDN_AUTH_KEY"
            environment variable has not been set
    """
    frontend_base_url: str = _get_frontend_base_url()
    cdn_auth_key: str = get_cdn_auth_key()
    frontend_crawler = FrontEndCrawler.create_crawler_for_cache_refresh(
        frontend_base_url=frontend_base_url, cdn_auth_key=cdn_auth_key
    )
    frontend_crawler.process_all_pages()
