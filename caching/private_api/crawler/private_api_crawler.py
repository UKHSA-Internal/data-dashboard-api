import logging
import re
from typing import Self

from caching.internal_api_client import InternalAPIClient
from caching.private_api.crawler.cms_blocks import CMSBlockParser
from caching.private_api.crawler.geographies_crawler import GeographiesAPICrawler
from caching.private_api.crawler.headless_cms_api import HeadlessCMSAPICrawler
from caching.private_api.crawler.request_payload_builder import RequestPayloadBuilder
from caching.private_api.crawler.type_hints import (
    CHART_DOWNLOAD,
    CMS_COMPONENT_BLOCK_TYPE,
)
from cms.common.models import CommonPage
from cms.home.models import HomePage
from cms.topic.models import TopicPage

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

    def __init__(self, internal_api_client: InternalAPIClient | None = None):
        self._internal_api_client = internal_api_client or InternalAPIClient()
        self._cms_block_parser = CMSBlockParser()
        self._geography_api_crawler = GeographiesAPICrawler(
            internal_api_client=self._internal_api_client
        )
        self._headless_cms_api_crawler = HeadlessCMSAPICrawler(
            internal_api_client=self._internal_api_client
        )
        self._request_payload_builder = RequestPayloadBuilder()

    # Class constructors

    @classmethod
    def create_crawler_for_cache_checking_only(cls) -> Self:
        internal_api_client = InternalAPIClient(cache_check_only=True)
        return cls(internal_api_client=internal_api_client)

    @classmethod
    def create_crawler_for_force_cache_refresh(cls) -> Self:
        internal_api_client = InternalAPIClient(force_refresh=True)
        return cls(internal_api_client=internal_api_client)

    @classmethod
    def create_crawler_for_lazy_loading(cls) -> Self:
        internal_api_client = InternalAPIClient(
            force_refresh=False, cache_check_only=False
        )
        return cls(internal_api_client=internal_api_client)

    # Process pages for content

    def process_pages(self, pages: list[HomePage, TopicPage, CommonPage]) -> None:
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
        logger.info("Completed processing of headless CMS API")

        self._geography_api_crawler.process_geographies_api()
        logger.info(
            "Completed processing of geographies API, now handling content blocks"
        )

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

    def process_all_sections_in_page(self, page: HomePage | TopicPage) -> None:
        """Makes requests to each individual content item within each section of the given `page`

        Args:
            page: The `Page` instance to be processed

        Returns:
            None

        """
        for section in page.body.raw_data:
            self.process_section(section=section)

    def process_section(self, section: dict[list[CMS_COMPONENT_BLOCK_TYPE]]) -> None:
        """Makes requests to each individual content item within the given `section`

        Args:
            section: The `dict containing the CMS information
                about the section contents

        Returns:
            None

        """
        content_cards = self._cms_block_parser.get_content_cards_from_section(
            section=section
        )

        # Gather all headline number row cards in this section of the page
        headline_numbers_row_cards = (
            self._cms_block_parser.get_headline_numbers_row_cards_from_content_cards(
                content_cards=content_cards
            )
        )
        # Process each of the headline number row cards which were gathered
        self.process_all_headline_numbers_row_cards(
            headline_numbers_row_cards=headline_numbers_row_cards
        )

        # Gather all chart row cards in this section of the page
        chart_row_cards = self._cms_block_parser.get_chart_row_cards_from_content_cards(
            content_cards=content_cards
        )
        # Process each of the chart row cards which were gathered
        self.process_all_chart_cards(chart_row_cards=chart_row_cards)

    # Process cards

    def process_headline_numbers_row_card(
        self, headline_numbers_row_card: CMS_COMPONENT_BLOCK_TYPE
    ) -> None:
        """Makes the relevant requests for the given single `headline_numbers_row_card`

        Args:
            headline_numbers_row_card: the headliner number row card CMS information

        Returns:
            None

        """
        headline_number_columns = headline_numbers_row_card["value"]["columns"]

        for column in headline_number_columns:
            for headline_number_block in column["value"]["rows"]:
                self.process_any_headline_number_block(
                    headline_number_block=headline_number_block
                )

    def process_all_headline_numbers_row_cards(
        self, headline_numbers_row_cards: list[CMS_COMPONENT_BLOCK_TYPE]
    ) -> None:
        for headline_numbers_row_card in headline_numbers_row_cards:
            self.process_headline_numbers_row_card(
                headline_numbers_row_card=headline_numbers_row_card
            )

    def process_all_chart_cards(
        self, chart_row_cards: list[CMS_COMPONENT_BLOCK_TYPE]
    ) -> None:
        for chart_row_card in chart_row_cards:
            chart_card_columns = chart_row_card["value"]["columns"]
            for chart_card in chart_card_columns:
                self.process_any_chart_card(
                    chart_card=chart_card,
                )

    # Process blocks

    def process_any_headline_number_block(
        self, headline_number_block: CMS_COMPONENT_BLOCK_TYPE
    ) -> None:
        """Makes the relevant requests for the given single `headline_number_block`

        Args:
            headline_number_block: The headline number block CMS information.
                This can be of the following types:
                    - "trend_number"
                    - "headline_number"
                    - "percentage_number"

        Returns:
            None

        Raises:
            `ValueError`: If an unrecognised block type is given

        """
        match headline_number_block["type"]:
            case "trend_number":
                self.process_trend_number_block(
                    trend_number_block=headline_number_block
                )
            case "headline_number":
                self.process_headline_number_block(
                    headline_number_block=headline_number_block
                )
            case "percentage_number":
                self.process_headline_number_block(
                    headline_number_block=headline_number_block
                )
            case _:
                raise ValueError

    def process_any_chart_card(self, chart_card: CMS_COMPONENT_BLOCK_TYPE) -> None:
        """Makes the relevant requests for the given single `chart_card`

        Args:
            chart_card: The chart block CMS information.
                This can be of the following types:
                    - "chart_card"
                    - "chart_with_headline_and_trend_card"

        Returns:
            None

        Raises:
            `ValueError`: If an unrecognised block type is given

        """
        match chart_card["type"]:
            case "chart_card":
                self.process_chart_block(chart_block=chart_card)
            case "chart_with_headline_and_trend_card":
                self.process_chart_with_headline_and_trend_card(
                    chart_with_headline_and_trend_card=chart_card,
                )
            case _:
                raise ValueError

    def process_chart_with_headline_and_trend_card(
        self,
        chart_with_headline_and_trend_card: CMS_COMPONENT_BLOCK_TYPE,
    ) -> None:
        """Makes the relevant requests for the given single `chart_with_headline_and_trend_card`

        Notes:
            This will handle the requests
            for each of the content items within the card.
            This includes the chart as well as any
            headline number elements

        Args:
            chart_with_headline_and_trend_card: The chart block CMS information.

        Returns:
            None

        Raises:
            `ValueError`: If an unrecognised block type is given

        """
        self.process_chart_block(
            chart_block=chart_with_headline_and_trend_card,
        )

        headline_number_columns = chart_with_headline_and_trend_card["value"][
            "headline_number_columns"
        ]
        for headline_number_block in headline_number_columns:
            self.process_any_headline_number_block(
                headline_number_block=headline_number_block
            )

    # Process individual blocks

    def process_chart_block(self, chart_block: CMS_COMPONENT_BLOCK_TYPE) -> None:
        """Makes the relevant requests for the given single `chart_block`

        Notes:
            This will handle the requests for the chart block within the card.
            This will also handle the request required
            for the accompanying table and download.

            For the chart itself, 2 requests will be made.
            1 for the double width chart, 1100.
            And another for the single width chart, 515

        Args:
            chart_block: The chart block CMS information.

        Returns:
            None

        """
        chart_block_value = chart_block["value"]

        self._process_table_for_chart_block(chart_block=chart_block_value)
        self._process_download_for_chart_block(
            chart_block=chart_block_value, file_format="csv"
        )

        self._process_chart_for_both_possible_widths(chart_block=chart_block)

    def _process_table_for_chart_block(self, chart_block: dict):
        tables_data = self._request_payload_builder.build_tables_request_data(
            chart_block=chart_block
        )
        self._internal_api_client.hit_tables_endpoint(data=tables_data)

    def _process_download_for_chart_block(self, chart_block: dict, file_format: str):
        downloads_data = self._request_payload_builder.build_downloads_request_data(
            chart_block=chart_block, file_format=file_format
        )
        return self._internal_api_client.hit_downloads_endpoint(data=downloads_data)

    def _process_chart_for_both_possible_widths(
        self, chart_block: CMS_COMPONENT_BLOCK_TYPE
    ) -> None:
        """Makes the relevant requests for the given single `chart_block`

        Notes:
            For the chart block, 2 requests will be made.
            1 for the double width chart, 1100.
            And another for the single width chart, 515

        Args:
            chart_block: The chart block CMS information.

        Returns:
            None

        """
        for chart_is_double_width in (True, False):
            charts_data = self._request_payload_builder.build_chart_request_data(
                chart_block=chart_block["value"],
                chart_is_double_width=chart_is_double_width,
            )
            self._internal_api_client.hit_charts_endpoint(data=charts_data)

    def process_headline_number_block(
        self, headline_number_block: CMS_COMPONENT_BLOCK_TYPE
    ) -> None:
        """Makes the relevant requests for the given single `headline_number_block`

        Args:
            headline_number_block: The headline number
                block CMS information.

        Returns:
            None

        """
        data = self._request_payload_builder.build_headlines_request_data(
            headline_number_block=headline_number_block["value"]
        )
        self._internal_api_client.hit_headlines_endpoint(data=data)

    def process_trend_number_block(
        self, trend_number_block: CMS_COMPONENT_BLOCK_TYPE
    ) -> None:
        """Makes the relevant requests for the given single `trend_number_block`

        Args:
            trend_number_block: The trend number block CMS information.

        Returns:
            None

        """
        data = self._request_payload_builder.build_trend_request_data(
            trend_number_block=trend_number_block["value"]
        )
        self._internal_api_client.hit_trends_endpoint(data=data)

    # Building request data

    # process downloads

    @staticmethod
    def format_titles_for_filenames(file_name: str) -> str:
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

    def create_directory_name_for_downloads(self, file_name: str) -> str:
        """Creates a directory name for bulk_download

        Args:
            file_name: String, unformatted filename.

        Returns:
            Formatted directory name.
        """
        file_name = "landing page" if file_name == "UKHSA data dashboard" else file_name
        return self.format_titles_for_filenames(file_name)

    def create_filename_for_chart_card(
        self,
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
        return f"{self.format_titles_for_filenames(file_name)}.{file_format}"

    def get_downloads_from_chart_row_columns(
        self,
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
            response = self._process_download_for_chart_block(
                chart_block=chart_card_content, file_format=file_format
            )
            downloads.append({"name": filename, "content": response.content})

        return downloads

    def get_downloads_from_chart_cards(
        self,
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
        pages: [HomePage, TopicPage, CommonPage],
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
                            page.title
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
