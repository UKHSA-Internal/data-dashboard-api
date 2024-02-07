from urllib.parse import quote_plus, urljoin


class FrontEndURLBuilder:
    """This is used by the `FrontEndCrawler` to construct URLs to send GET requests to all relevant pages"""

    def __init__(self, base_url: str):
        self._base_url = base_url

    def build_url_for_topic_page(self, slug: str) -> str:
        """Builds the full URL for the given topic page `slug`

        Args:
            slug: The slug associated with the Topic page

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._base_url, f"/topics/{slug}")

    def build_url_for_common_page(self, slug: str) -> str:
        """Builds the full URL for the given common page `slug`

        Args:
            slug: The slug associated with the Common page

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._base_url, slug)

    def build_url_for_home_page(self) -> str:
        """Builds the full URL for the single home page

        Returns:
            The full URL which can be passed to requests

        """
        return self._base_url

    def build_url_for_whats_new_parent_page(self) -> str:
        """Builds the full URL for the single what's new parent page

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._base_url, "whats-new")

    def build_url_for_whats_new_child_entry(self, slug: str) -> str:
        """Builds the full URL for the single what's new child entry

        Args:
            slug: The slug associated with the `WhatsNewChildEntry`

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._base_url, f"whats-new/{slug}")

    def build_url_for_metrics_documentation_parent_page(self) -> str:
        """Builds the full URL for the single metrics documentation parent page

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._base_url, "metrics-documentation")

    def build_url_for_metrics_documentation_child_entry(self, slug: str) -> str:
        """Builds the full URL for the single metrics documentation child entry

        Args:
            slug: The slug associated with the `MetricsDocumentationChildEntry`

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._base_url, f"metrics-documentation/{slug}")

    def build_url_for_feedback_confirmation_page(self) -> str:
        """Builds the full URL for the feedback confirmation page

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._base_url, "/feedback/confirmation")

    @staticmethod
    def build_query_params_for_area_selector_page(
        geography_type_name: str, geography_name: str
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
