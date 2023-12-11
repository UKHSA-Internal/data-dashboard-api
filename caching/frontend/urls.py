from urllib.parse import urljoin


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
        return urljoin(self._base_url, "metrics_documentation")

    def build_url_for_metrics_documentation_child_entry(self, slug: str) -> str:
        """Builds the full URL for the single metrics documentation child entry

        Args:
            slug: The slug associated with the `MetricsDocumentationChildEntry`

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._base_url, f"metrics_documentation/{slug}")

    def build_url_for_feedback_confirmation_page(self) -> str:
        """Builds the full URL for the feedback confirmation page

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._base_url, "/feedback/confirmation")
