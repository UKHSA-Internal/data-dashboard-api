import logging
from typing import Self

from caching.internal_api_client import InternalAPIClient
from cms.common.models import CommonPage
from cms.home.models import HomePage
from cms.topic.models import TopicPage

CMS_COMPONENT_BLOCK_TYPE = dict[str, str | dict[str, str] | list[dict[str, str]]]


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

    # Class constructors

    @classmethod
    def create_crawler_for_cache_checking_only(cls) -> Self:
        internal_api_client = InternalAPIClient(cache_check_only=True)
        return cls(internal_api_client=internal_api_client)

    @classmethod
    def create_crawler_for_force_cache_refresh(cls) -> Self:
        internal_api_client = InternalAPIClient(force_refresh=True)
        return cls(internal_api_client=internal_api_client)

    # Process headless CMS API

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
        self, pages: list[HomePage, TopicPage]
    ) -> None:
        """Makes a request to the headless CMS API detail `pages/` endpoint for each of the given `pages`

        Returns:
            None

        """
        for page in pages:
            self.process_individual_page_for_headless_cms_api(page=page)

    def process_individual_page_for_headless_cms_api(
        self, page: HomePage | TopicPage
    ) -> None:
        """Makes a request to the headless CMS API detail `pages/` endpoint for the given `page`

        Returns:
            None

        """
        logger.info("Hitting GET pages/ endpoint for `%s` page", page.title)
        self._internal_api_client.hit_pages_detail_endpoint(page_id=page.id)

    # Process pages for content

    def get_all_downloads(self, pages: list[HomePage, TopicPage]) -> None:
        downloads = []
        for page in pages:
            try:
                for section in page.body.raw_data:
                    content_cards = self.get_content_cards_from_section(section=section)
                    # Gather all chart row cards in this section of the page
                    chart_row_cards = self.get_chart_row_cards_from_content_cards(
                        content_cards=content_cards
                    )
                    # Process each of the chart row cards which were gathered
                    extracted_downloads = self.process_all_chart_cards_for_downloads(chart_row_cards=chart_row_cards)
                    downloads += extracted_downloads

            except AttributeError:
                pass
        return downloads

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
        self.process_list_pages_for_headless_cms_api()
        self.process_detail_pages_for_headless_cms_api(pages=pages)
        logger.info(
            "Completed processing of headless CMS API, now handling content blocks"
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
        content_cards = self.get_content_cards_from_section(section=section)

        # Gather all headline number row cards in this section of the page
        headline_numbers_row_cards = (
            self.get_headline_numbers_row_cards_from_content_cards(
                content_cards=content_cards
            )
        )
        # Process each of the headline number row cards which were gathered
        self.process_all_headline_numbers_row_cards(
            headline_numbers_row_cards=headline_numbers_row_cards
        )

        # Gather all chart row cards in this section of the page
        chart_row_cards = self.get_chart_row_cards_from_content_cards(
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

    def process_all_chart_cards_for_downloads(
            self, chart_row_cards: list[CMS_COMPONENT_BLOCK_TYPE]
    ) -> None:
        downloads = []

        for chart_row_card in chart_row_cards:
            chart_card_columns = chart_row_card["value"]["columns"]
            for chart_card in chart_card_columns:
                chart_block_value = chart_card["value"]

                name = f"{chart_block_value['title']}.csv"
                response = self._process_download_for_chart_block(chart_block=chart_block_value)
                downloads.append({"name": name, "content": response.content})

        return downloads

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
        self._process_download_for_chart_block(chart_block=chart_block_value)

        self._process_chart_for_both_possible_widths(chart_block=chart_block)

    def _process_table_for_chart_block(self, chart_block: dict):
        tables_data = self._build_tables_request_data(chart_block=chart_block)
        self._internal_api_client.hit_tables_endpoint(data=tables_data)

    def _process_download_for_chart_block(self, chart_block: dict):
        downloads_data = self._build_downloads_request_data(chart_block=chart_block)
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
            charts_data = self._build_chart_request_data(
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
        data = self._build_headlines_request_data(
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
        data = self._build_trend_request_data(
            trend_number_block=trend_number_block["value"]
        )
        self._internal_api_client.hit_trends_endpoint(data=data)

    # Deconstruct blocks

    @staticmethod
    def get_content_cards_from_section(
        section: dict[list[CMS_COMPONENT_BLOCK_TYPE]],
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Filters for a list of content cards from the given `section`

        Args:
            section: The section dict from the CMS

        Returns:
            A list of content card dicts

        """
        return section["value"]["content"]

    @staticmethod
    def get_chart_row_cards_from_content_cards(
        content_cards: list[CMS_COMPONENT_BLOCK_TYPE],
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Filters for a list of chart row from the given `content_cards`

        Args:
            content_cards: The list of content card dicts
                from the CMS

        Returns:
            A list of chart row card dicts which can be processed

        """
        return [
            content_card
            for content_card in content_cards
            if content_card["type"] == "chart_row_card"
        ]

    @staticmethod
    def get_headline_numbers_row_cards_from_content_cards(
        content_cards: list[CMS_COMPONENT_BLOCK_TYPE],
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Filters for a list of headliner number row cards from the given `content_cards`

        Args:
            content_cards: The list of content card dicts
                from the CMS

        Returns:
            A list of headline number row card dicts
            which can be processed

        """
        return [
            content_card
            for content_card in content_cards
            if content_card["type"] == "headline_numbers_row_card"
        ]

    # Building request data

    @staticmethod
    def _build_headlines_request_data(
        headline_number_block: dict[str, str]
    ) -> dict[str, str]:
        """Builds the headlines endpoint request payload from the given `headline_number_block`

        Args:
            headline_number_block: The headline number block
                from the CMS

        Returns:
            A dict which can be used as the payload to the
            `headlines` endpoint

        """
        return {
            "topic": headline_number_block["topic"],
            "metric": headline_number_block["metric"],
            "geography": headline_number_block.get("geography", "England"),
            "geography_type": headline_number_block.get("geography_type", "Nation"),
            "sex": headline_number_block.get("sex", "all"),
            "age": headline_number_block.get("age", "all"),
            "stratum": headline_number_block.get("stratum", "default"),
        }

    @staticmethod
    def _build_trend_request_data(trend_number_block: dict[str, str]) -> dict[str, str]:
        """Builds the trends endpoint request payload from the given `trend_number_block`

        Args:
            trend_number_block: The trends number block from the CMS

        Returns:
            A dict which can be used as the payload to the
            `trends` endpoint

        """
        return {
            "topic": trend_number_block["topic"],
            "metric": trend_number_block["metric"],
            "percentage_metric": trend_number_block["percentage_metric"],
        }

    def _build_chart_request_data(
        self, chart_block: CMS_COMPONENT_BLOCK_TYPE, chart_is_double_width: bool
    ) -> dict[str, str | int, list[dict[str, str]]]:
        """Builds the charts endpoint request payload from the given `chart_block`

        Args:
            chart_block: The chart block from the CMS
            chart_is_double_width: If True, a chart width of 1100 is applied.
                If False, a chart width of 515 is applied.

        Returns:
            A dict which can be used as the payload to the
            `charts` endpoint

        """
        return {
            "plots": [
                self._build_plot_data(plot_value=plot["value"])
                for plot in chart_block["chart"]
            ],
            "file_format": "svg",
            "chart_width": 1100 if chart_is_double_width else 515,
            "chart_height": 260,
            "x_axis": chart_block.get("x_axis", ""),
            "y_axis": chart_block.get("y_axis", ""),
        }

    @staticmethod
    def _build_plot_data(plot_value: dict[str, str]) -> dict[str, str]:
        """Builds the individual plot data from the given `plot_value`

        Args:
            plot_value: The dict containing the plot data

        Returns:
            A dict which can be used to represent the individual plot
            within the `plots` list of the payload
            to the `charts` or `tables` endpoint

        """
        return {
            "topic": plot_value["topic"],
            "metric": plot_value["metric"],
            "chart_type": plot_value["chart_type"],
            "stratum": plot_value["stratum"],
            "geography": plot_value["geography"],
            "geography_type": plot_value["geography_type"],
            "sex": plot_value["sex"],
            "age": plot_value["age"],
            "date_from": plot_value["date_from"],
            "date_to": plot_value["date_to"],
            "label": plot_value["label"],
            "line_colour": plot_value["line_colour"],
            "line_type": plot_value["line_type"],
        }

    def _build_tables_request_data(
        self, chart_block: CMS_COMPONENT_BLOCK_TYPE
    ) -> dict[str, str | int, list[dict[str, str]]]:
        """Builds the tables endpoint request payload from the given `chart_block`

        Args:
            chart_block: The chart block from the CMS

        Returns:
            A dict which can be used as the payload to the
            `tables` endpoint

        """
        return {
            "plots": [
                self._build_plot_data(plot_value=plot["value"])
                for plot in chart_block["chart"]
            ],
            "x_axis": chart_block["x_axis"],
            "y_axis": chart_block["y_axis"],
        }

    def _build_downloads_request_data(
        self, chart_block: CMS_COMPONENT_BLOCK_TYPE
    ) -> dict[str, str | int, list[dict[str, str]]]:
        """Builds the tables endpoint request payload from the given `chart_block`

        Args:
            chart_block: The chart block from the CMS

        Returns:
            A dict which can be used as the payload to the
            `tables` endpoint

        """
        return {
            "plots": [
                self._build_downloads_plot_data(plot_value=plot["value"])
                for plot in chart_block["chart"]
            ],
            "file_format": "csv",
        }

    @staticmethod
    def _build_downloads_plot_data(plot_value: dict[str, str]) -> dict[str, str]:
        """Builds the individual downloadable plot data from the given `plot_value`

        Args:
            plot_value: The dict containing the plot data

        Returns:
            A dict which can be used to represent the individual plot
            within the `plots` list of the payload
            to the `downloads` endpoint only

        """
        return {
            "topic": plot_value["topic"],
            "metric": plot_value["metric"],
            "date_from": plot_value["date_from"],
            "date_to": plot_value["date_to"],
            "stratum": plot_value["stratum"],
            "geography": plot_value["geography"],
            "geography_type": plot_value["geography_type"],
            "sex": plot_value["sex"],
            "age": plot_value["age"],
        }
