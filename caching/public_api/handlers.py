import os

from caching.public_api.crawler import PublicAPICrawler


def _get_public_api_url() -> str:
    """Returns the value of the "PUBLIC_API_URL" environment variable

    Returns:
        The value of the "PUBLIC_API_URL"

    Raises:
        `KeyError`: If the "PUBLIC_API_URL" has not been set

    """
    try:
        return os.environ["PUBLIC_API_URL"]
    except KeyError as error:
        raise KeyError("No `PUBLIC_API_URL` provided") from error


def get_cdn_auth_key() -> str:
    """Returns the value of the "CDN_AUTH_KEY" environment variable

    Returns:
        The value of the "CDN_AUTH_KEY"

    Raises:
        `KeyError`: If the "CDN_AUTH_KEY" has not been set

    """
    try:
        cdn_auth_key = os.environ["CDN_AUTH_KEY"]
    except KeyError as error:
        raise KeyError("No CDN auth key specified") from error
    return f'"{cdn_auth_key}"'


def crawl_public_api() -> None:
    """Traverse all relevant endpoints on the public API

    Notes:
        Currently this will only traverse the mandatory URL parameters.
        The section of the API controlled by query parameters is not being crawled.

    Returns:
        None

    Raises:
        `KeyError`: If either `PUBLIC_API_URL` or `CDN_AUTH_KEY`
            environment variables are not provided

    """
    public_api_base_url: str = _get_public_api_url()
    cdn_auth_key: str = get_cdn_auth_key()
    public_api_crawler = PublicAPICrawler.create_crawler_for_cache_refresh(
        public_api_base_url=public_api_base_url, cdn_auth_key=cdn_auth_key
    )
    public_api_crawler.process_all_routes()
