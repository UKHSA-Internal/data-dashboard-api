import urllib.parse
from types import ModuleType

import requests


class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    @property
    def revalidate_url(self) -> str:
        return urllib.parse.urljoin(self.base_url, "api/revalidate")

    def _get_request(self, url, **kwargs):
        """Sends a get request, injecting the API key into the params in the process

        Args:
            url: The URL to which to send the GET request to

        Returns:
            `requests.Response`: The response sent back from the server.

        """
        params = kwargs.pop("params", {})
        params["secret"] = self.api_key
        return requests.get(url=url, params=params, **kwargs)

    def send_request_to_revalidate_page(self, slug: str) -> requests.Response:
        """Sends a request to the `api/revalidate` endpoint for the given `slug`

        Args:
            slug: The associated slug value of the Page.
                E.g. For the "About" page, the slug value would be `about

        Returns:
            `requests.Response`: The response sent back from the server.

        """
        return self._get_request(url=self.revalidate_url, params={"slug": slug})


def revalidate_page_via_api_client(config: ModuleType, slug: str) -> None:
    """Calls the frontend API client to request the revalidation of the page denoted by the given `slug`

    Notes
    Under the hood, the `requests` library will throw a `MissingSchema` error
    when trying to send a request to a URL of "".
    If the `FRONTEND_API_URL` & `FRONTEND_API_KEY` env vars are not set,
    then the resulting error will be silenced.

    Args:
        config: The object which contains the following attributes:
            `FRONTEND_API_URL` and `FRONTEND_API_KEY`
        slug: The associated slug value of the Page.
            E.g. For the "About" page, the slug value would be `about

    Returns:
        None

    """
    api_client = APIClient(
        base_url=config.FRONTEND_API_URL, api_key=config.FRONTEND_API_KEY
    )
    try:
        api_client.send_request_to_revalidate_page(slug=slug)
    except requests.exceptions.MissingSchema:
        print(f"Front end integration not configured. Revalidation will not be made.")
