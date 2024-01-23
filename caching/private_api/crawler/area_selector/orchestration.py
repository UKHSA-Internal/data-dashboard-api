import logging
import time

from caching.private_api.crawler import PrivateAPICrawler
from caching.private_api.crawler.area_selector.concurrency import (
    call_with_star_map_multiprocessing,
)
from caching.private_api.crawler.geographies_crawler import (
    GeographiesAPICrawler,
    GeographyData,
)
from cms.topic.models import TopicPage

logger = logging.getLogger(__name__)


class AreaSelectorOrchestrator:
    """Responsible for spinning up instances of the `PrivateAPICrawler` to process geography/page combinations"""

    def __init__(self, geographies_api_crawler: GeographiesAPICrawler):
        self._geographies_api_crawler = geographies_api_crawler

    def get_all_geography_combinations(self) -> list[GeographyData]:
        """Returns all the available geographies as enriched `GeographyData` models

        Returns:
            List of `GeographyData` containing the name
            and corresponding geography type name for each geography

        """
        return [
            geography_data
            for geography_type_data in self._geographies_api_crawler.process_geographies_api()
            for geography_data in geography_type_data.export_all_geography_combinations()
        ]

    def process_pages(self, pages: list[TopicPage]) -> None:
        """Delegates each valid geography/page combination to a dedicated `PrivateAPICrawler` to be processed

        Args:
            pages: List of `TopicPage` models which are to be processed

        Returns:
            None

        """
        all_geography_combinations = self.get_all_geography_combinations()

        for page in pages:
            self.parallel_process_all_geography_combinations_for_page(
                geography_combinations=all_geography_combinations,
                page=page,
            )

    @classmethod
    def parallel_process_all_geography_combinations_for_page(
        cls, geography_combinations: list[GeographyData], page: TopicPage
    ) -> None:
        """Process all `geography_combinations` in parallel for the given `page`

        Notes:
            This will spin up N number of processes on the host machine
            in order to parallelize the processing of the geography/page combinations.

        Args:
            geography_combinations: List of enriched `GeographyData` models
                representing each individual geography combination
            page: The `Page` model object to be processed.
                Currently, this is only expected to be a `TopicPage` type

        Returns:
            None

        """
        start_time = time.time()

        args = [(geography_data, page.id) for geography_data in geography_combinations]
        call_with_star_map_multiprocessing(
            func=cls.process_geography_page_combination,
            items=args,
        )

        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)

        logger.info(
            "Finished processing all geographies for `%s` page in %s seconds",
            page.title,
            elapsed_time,
        )

    @classmethod
    def process_geography_page_combination(
        cls, geography_data: GeographyData, page_id: int
    ) -> None:
        """Processes the individual `geography_data` and `page_id` combination with a new `PrivateAPICrawler` instance

        Notes:
            The created `PrivateAPICrawler` will be set to forcibly refresh the cache
            if the cache key is found.
            So it will overwrite the cache keys that it comes across.

            The `page_id` parameter is provided as an ID and not the `Page` object itself
            so that it can be either:
                a) picklable by the multiprocessing library
                b) serializable as a message to a queue

        Args:
            geography_data: An enriched `GeographyData` model
                for an individual geography combination
            page_id: The ID of the page which is to be processed

        Returns:
            None

        """
        private_api_crawler = PrivateAPICrawler.create_crawler_for_force_cache_refresh()

        # Since the payload to this method is intended to be serializable
        # via pickle -> multiprocessing or a message broker of some sort
        # the arguments remain as simple types.
        # Hence, the model manager dependency was not injected in.
        page = TopicPage.objects.get(id=page_id)
        private_api_crawler.process_all_sections_in_page(
            page=page, geography_data=geography_data
        )
