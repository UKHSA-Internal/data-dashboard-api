from urllib.parse import quote_plus, urljoin


class FrontEndURLBuilder:
    """This is used by the `FrontEndCrawler` to construct URLs to send GET requests to all relevant pages"""

    def __init__(self, *, base_url: str):
        self._base_url = base_url

    def build_url_for_topic_page(self, *, slug: str) -> str:
        """Builds the full URL for the given topic page `slug`

        Args:
            slug: The slug associated with the Topic page

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._base_url, f"/topics/{slug}")

    def build_url_for_sitemap(self) -> str:
        """Builds the full URL for the sitemap page

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._base_url, "/sitemap.xml")

    @staticmethod
    def build_query_params_for_area_selector_page(
        *, geography_type_name: str, geography_name: str
    ) -> dict[str, str]:
        """Creates a dict of query parameters of URL quoted params

        Args:
            geography_type_name: The name of the
                geography type/area type
            geography_name:  The name of the geography/area

        Returns:
            Dict representing the query parameters
            which can then be passed to the request

        """
        geography_name: str = quote_plus(string=geography_name)
        geography_type_name: str = quote_plus(string=geography_type_name)
        return {"areaType": geography_type_name, "areaName": geography_name}
