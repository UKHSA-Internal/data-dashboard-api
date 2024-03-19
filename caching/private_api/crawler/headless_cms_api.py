import logging

from caching.internal_api_client import InternalAPIClient
from cms.home.models import HomePage
from cms.topic.models import TopicPage

logger = logging.getLogger(__name__)


class HeadlessCMSAPICrawler:
    """Crawls the headless CMS `pages` API for all available pages"""

    def __init__(self, *, internal_api_client: InternalAPIClient):
        self._internal_api_client = internal_api_client

    def process_list_pages_for_headless_cms_api(self) -> None:
        """Makes a request to the headless CMS API list `pages/` endpoint

        Returns:
            None

        """
        logger.info("Hitting list GET pages/ endpoint")
        self._internal_api_client.hit_pages_list_endpoint()

        logger.info("Hitting list GET pages/ endpoint for all page types")
        self._internal_api_client.hit_pages_list_endpoint_for_all_page_types()

    def process_detail_pages_for_headless_cms_api(
        self, *, pages: list[HomePage, TopicPage]
    ) -> None:
        """Makes a request to the headless CMS API detail `pages/` endpoint for each of the given `pages`

        Returns:
            None

        """
        for page in pages:
            self.process_individual_page_for_headless_cms_api(page=page)

    def process_individual_page_for_headless_cms_api(
        self, *, page: HomePage | TopicPage
    ) -> None:
        """Makes a request to the headless CMS API detail `pages/` endpoint for the given `page`

        Returns:
            None

        """
        logger.info("Hitting GET pages/ endpoint for `%s` page", page.title)
        self._internal_api_client.hit_pages_detail_endpoint(page_id=page.id)
