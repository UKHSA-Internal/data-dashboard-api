import urllib.parse

import requests


class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def _get_request(self, url, **kwargs):
        params = kwargs.pop("params", {})
        params["secret"] = self.api_key
        return requests.get(url=url, params=params, **kwargs)

    @property
    def revalidate_url(self) -> str:
        return urllib.parse.urljoin(self.base_url, "api/revalidate")

    def send_request_to_revalidate_page(self, slug: str) -> requests.Response:
        return self._get_request(url=self.revalidate_url, params={"slug": slug})
