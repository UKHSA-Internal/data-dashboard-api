import urllib.parse

import requests


class APIClient:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key

    def _get_request(self, **kwargs):
        params = kwargs.pop("params", {})
        params["secret"] = self.key
        return requests.get(**kwargs, params=params)

    @property
    def revalidate_url(self) -> str:
        return urllib.parse.urljoin(self.url, "api/revalidate")

    def send_request_to_revalidate_page(self, slug: str) -> requests.Response:
        return self._get_request(url=self.revalidate_url, params={"slug": slug})
