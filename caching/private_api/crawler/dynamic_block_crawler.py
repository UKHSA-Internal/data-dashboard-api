from caching.internal_api_client import InternalAPIClient
from caching.private_api.crawler.request_payload_builder import RequestPayloadBuilder
from caching.private_api.crawler.type_hints import CMS_COMPONENT_BLOCK_TYPE


class DynamicContentBlockCrawler:
    def __init__(self, internal_api_client: InternalAPIClient):
        self._internal_api_client = internal_api_client
        self._request_payload_builder = RequestPayloadBuilder()

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
        self.process_download_for_chart_block(
            chart_block=chart_block_value, file_format="csv"
        )

        self._process_chart_for_both_possible_widths(chart_block=chart_block)

    def _process_table_for_chart_block(self, chart_block: dict):
        tables_data = self._request_payload_builder.build_tables_request_data(
            chart_block=chart_block
        )
        self._internal_api_client.hit_tables_endpoint(data=tables_data)

    def process_download_for_chart_block(self, chart_block: dict, file_format: str):
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
