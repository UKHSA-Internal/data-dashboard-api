import logging
import re
from typing import Self

import django

django.setup()
# File descriptors & db connections are not copied from the parent
# as they are when `forking` instead of `spawning`.
# So `django.setup()` is required prior to any models being imported
# This is because we spawn multiple processes when crawling the private API
# for all the available geography combinations.

from caching.common.geographies_crawler import (  # noqa: E402
    GeographiesAPICrawler,
    GeographyData,
)
from caching.internal_api_client import InternalAPIClient  # noqa: E402
from caching.private_api.crawler.dynamic_block_crawler import (  # noqa: E402
    DynamicContentBlockCrawler,
)
from caching.private_api.crawler.headless_cms_api import (  # noqa: E402
    HeadlessCMSAPICrawler,
)
from caching.private_api.crawler.type_hints import (  # noqa: E402
    CHART_DOWNLOAD,
    CMS_COMPONENT_BLOCK_TYPE,
)
from cms.common.models import CommonPage  # noqa: E402
from cms.dynamic_content.blocks_deconstruction import CMSBlockParser  # noqa: E402
from cms.topic.models import TopicPage  # noqa: E402

logger = logging.getLogger(__name__)


class PrivateAPICrawler:
    """This is used to parse the CMS blocks and fire off the corresponding requests

    Notes:
        Under the hood, this uses the `InternalAPIClient` to crawl the various endpoints.
        This makes the assumption that each of the following endpoints are wrapped with a cache:
        - charts
        - tables
        - headlines
        - trends

    """

    def __init__(
        self,
        *,
        internal_api_client: InternalAPIClient | None = None,
        cms_block_parser: CMSBlockParser | None = None,
        dynamic_content_block_crawler: DynamicContentBlockCrawler | None = None,
    ):
        self._internal_api_client = internal_api_client or InternalAPIClient()
        self.geography_api_crawler = GeographiesAPICrawler(
            internal_api_client=self._internal_api_client
        )
        self._cms_block_parser = cms_block_parser or CMSBlockParser()
        self._headless_cms_api_crawler = HeadlessCMSAPICrawler(
            internal_api_client=self._internal_api_client
        )
        self._dynamic_content_block_crawler = (
            dynamic_content_block_crawler
            or DynamicContentBlockCrawler(
                internal_api_client=self._internal_api_client,
            )
        )

    # Class constructors

    @classmethod
    def create_crawler_to_force_write_in_non_reserved_namespace(cls) -> Self:
        internal_api_client = InternalAPIClient(
            force_refresh=True, reserved_namespace=False
        )
        return cls(internal_api_client=internal_api_client)

    @classmethod
    def create_crawler_to_force_write_in_reserved_staging_namespace(cls) -> Self:
        internal_api_client = InternalAPIClient(
            force_refresh=True, reserved_namespace=True
        )
        return cls(internal_api_client=internal_api_client)

    @classmethod
    def create_crawler_for_lazy_loading(cls) -> Self:
        internal_api_client = InternalAPIClient(force_refresh=False)
        return cls(internal_api_client=internal_api_client)

    # Process pages for content

    def process_pages(self, *, pages: list[TopicPage, CommonPage]) -> None:
        """Makes requests to each individual content item within each of the given `pages`

        Notes:
            This will also make requests to the headless CMS API `pages/` endpoints
            in order to cache the CMS content in line with the content.
            This is primarily so that the cached pages content is always in lockstep
            with the cached content items (charts, headlines, tables etc).

        Args:
            pages: List of `Page` instances to be processed

        Returns:
            None

        """
        self._headless_cms_api_crawler.process_list_pages_for_headless_cms_api()
        self._headless_cms_api_crawler.process_detail_pages_for_headless_cms_api(
            pages=pages
        )
        self._headless_cms_api_crawler.process_all_snippets()
        logger.info("Completed processing of headless CMS API")

        pages_count = len(pages)

        for index, page in enumerate(pages, 1):
            try:
                logger.info("Processing content blocks within `%s` page", page.title)
                self.process_all_sections_in_page(page=page)
            except AttributeError:
                logger.info(
                    "`%s` page has no dynamic content blocks. "
                    "So only the headless CMS API detail has been processed",
                    page.title,
                )
            logger.info("Completed %s / %s pages", index, pages_count)

    # Process sections

    def process_all_sections_in_page(
        self, *, page: TopicPage, geography_data: GeographyData | None = None
    ) -> None:
        """Makes requests to each individual content item within each section of the given `page`

        Args:
            page: The `Page` instance to be processed
            geography_data: The `GeographyData` describing
                the geography to apply to the given `page`
                If provided as None, then the original blocks
                throughout the `page` will be processed

        Returns:
            None

        """
        for section in page.body.raw_data:
            self.process_section(section=section, geography_data=geography_data)

    def process_section(
        self,
        *,
        section: dict[list[CMS_COMPONENT_BLOCK_TYPE]],
        geography_data: GeographyData | None = None,
    ) -> None:
        """Makes requests to each individual content item within the given `section`

        Args:
            section: The `dict containing the CMS information
                about the section contents
            geography_data: The `GeographyData` describing
                the geography to apply to the given `section`
                If provided as None, then the original blocks
                in the `section` will be processed

        Returns:
            None

        """
        # Gather all headline number blocks in this section of the page
        headline_number_blocks = (
            self._cms_block_parser.get_all_headline_blocks_from_section(section=section)
        )
        # Process each of the headline number blocks which were gathered
        self._dynamic_content_block_crawler.process_all_headline_number_blocks(
            headline_number_blocks=headline_number_blocks
        )

        # Gather all chart blocks in this section of the page
        chart_blocks = (
            self._cms_block_parser.get_all_chart_blocks_from_section_for_geography(
                section=section, geography_data=geography_data
            )
        )

        # Process each of the chart blocks which were gathered
        self._dynamic_content_block_crawler.process_all_chart_blocks(
            chart_blocks=chart_blocks
        )

    # process downloads

    @staticmethod
    def format_titles_for_filenames(*, file_name: str) -> str:
        """Formats a string to be used for filenames and directory names.

        Args:
            file_name: String, unformatted file / directory name.

        Returns:
            formatted file / directory name as a string.
        """
        words = file_name.split(" ")
        pattern = re.compile("[(+),/\\-{!'\\\\'&@%*;:^$£?|\".\\[\\]}]")
        formatted_words = list(filter(None, [pattern.sub(r"", word) for word in words]))

        return "_".join(formatted_words).lower()

    def create_directory_name_for_downloads(self, *, file_name: str) -> str:
        """Creates a directory name for bulk_download

        Args:
            file_name: String, unformatted filename.

        Returns:
            Formatted directory name.
        """
        file_name = "landing page" if file_name == "UKHSA data dashboard" else file_name
        return self.format_titles_for_filenames(file_name=file_name)

    def create_filename_for_chart_card(
        self,
        *,
        file_name: str,
        file_format: str,
    ) -> str:
        """Create filename for bulk download

        Args:
            file_name: String, unformatted filename.
            file_format: Filename extension

        Returns:
            Formatted file name and extension taken from file_format
        """
        return f"{self.format_titles_for_filenames(file_name=file_name)}.{file_format}"

    def get_downloads_from_chart_row_columns(
        self,
        *,
        chart_row_columns: list[CMS_COMPONENT_BLOCK_TYPE],
        file_format: str,
    ) -> list[CHART_DOWNLOAD]:
        """Get downloads from chart row columns

        Args:
            chart_row_columns: list of cms component blocks containing chart
                data for queries.
            file_format: The format for download response data.
                supports csv or json

        Returns:
            A list of dictionaries containing filenames and response content
            from the downloads endpoint.
        """
        downloads = []

        for chart_card in chart_row_columns:
            chart_card_content = chart_card["value"]
            filename = self.create_filename_for_chart_card(
                file_name=chart_card_content["title"], file_format=file_format
            )
            response = (
                self._dynamic_content_block_crawler.process_download_for_chart_block(
                    chart_block=chart_card_content, file_format=file_format
                )
            )
            downloads.append({"name": filename, "content": response.content})

        return downloads

    def get_downloads_from_chart_cards(
        self,
        *,
        chart_row_cards: list[CMS_COMPONENT_BLOCK_TYPE],
        file_format: str,
    ) -> list[CHART_DOWNLOAD]:
        """Get downloads from chart row cards

        Args:
            chart_row_cards: Chart row data that includes query parameters for the download endpoint.
            file_format: the file format for download response format csv or json

        Returns:
            A list of dictionaries containing a file name and response data
        """
        downloads = []

        for chart_row_card in chart_row_cards:
            chart_row_columns = chart_row_card["value"]["columns"]

            downloads.extend(
                self.get_downloads_from_chart_row_columns(
                    chart_row_columns=chart_row_columns, file_format=file_format
                )
            )

        return downloads

    def get_downloads_from_page_sections(
        self,
        *,
        sections: list[dict[list[CMS_COMPONENT_BLOCK_TYPE]]],
        file_format: str,
    ) -> list[CHART_DOWNLOAD]:
        """Get downloads from page sections, extracts chart row cards
            from page sections and downloads chart data.

        Args:
            sections: list of page sections containing chart data
            file_format: The request format for downloaded data.

        Returns:
           A list of dictionaries containing downloads data, which
           includes a filename and download response data.
        """
        downloads = []

        for section in sections:
            chart_row_cards = (
                self._cms_block_parser.get_chart_row_cards_from_page_section(
                    section=section
                )
            )

            downloads.extend(
                self.get_downloads_from_chart_cards(
                    chart_row_cards=chart_row_cards,
                    file_format=file_format,
                )
            )

        return downloads

    def get_all_downloads(
        self,
        *,
        pages: [TopicPage, CommonPage],
        file_format: str,
    ) -> list[CHART_DOWNLOAD]:
        """Get all chart downloads from supported pages.
            These include `HomePage` and `TopicPage`, unsupported pages are
            filtered out.

        Args:
            pages: A list of pages to process for downloads.
            file_format: the file_format for response data.

        Returns:
            A list of dictionaries containing filename and download content in
            either csv or json grouped by page name.
        """
        downloads = []

        for page in pages:
            try:
                downloads.append(
                    {
                        "directory_name": self.create_directory_name_for_downloads(
                            file_name=page.title
                        ),
                        "downloads": self.get_downloads_from_page_sections(
                            sections=page.body.raw_data, file_format=file_format
                        ),
                    }
                )
            except AttributeError:
                logger.info("Page %s does not contain chart data", page)
                continue

        return downloads
