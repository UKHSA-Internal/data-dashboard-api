import os

from caching.frontend.crawler import FrontEndCrawler
from caching.public_api.crawler import get_cdn_auth_key


def _get_frontend_base_url() -> str:
    """Returns the value of the "FRONTEND_URL" environment variable

    Returns:
        The value of the "FRONTEND_URL"

    Raises:
        `KeyError`: If the "FRONTEND_URL" has not been set

    """
    try:
        return os.environ["FRONTEND_URL"]
    except KeyError as error:
        raise KeyError("No `FRONTEND_URL` provided") from error


def crawl_front_end() -> None:
    """Traverse all relevant pages on the frontend

    Returns:
        None

    Raises:
        `KeyError`: If either `FRONTEND_URL` or `CDN_AUTH_KEY`
            environment variables are not provided

    """
    frontend_base_url: str = _get_frontend_base_url()
    cdn_auth_key: str = get_cdn_auth_key()
    frontend_crawler = FrontEndCrawler.create_crawler_for_cache_refresh(
        frontend_base_url=frontend_base_url, cdn_auth_key=cdn_auth_key
    )
    frontend_crawler.process_all_pages()
