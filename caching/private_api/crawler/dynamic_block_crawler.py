from caching.internal_api_client import InternalAPIClient
from caching.private_api.crawler.request_payload_builder import RequestPayloadBuilder
from caching.private_api.crawler.type_hints import CMS_COMPONENT_BLOCK_TYPE
from cms.dynamic_content.global_filter_deconstruction import GlobalFilterCMSBlockParser


class DynamicContentBlockCrawler:
    def __init__(self, *, internal_api_client: InternalAPIClient):
        self._internal_api_client = internal_api_client
        self._request_payload_builder = RequestPayloadBuilder()

    # Process all blocks

    def process_all_headline_number_blocks(
        self, *, headline_number_blocks: list[CMS_COMPONENT_BLOCK_TYPE]
    ) -> None:
        """Makes the relevant requests for the given `headline_number_blocks`

        Notes:
            This will handle the requests for all types of
            headline number elements, including:
            - "headline"
            - "percentage"
            - "trend"

        Args:
            headline_number_blocks: List of all headline number
                blocks on the page which are to be crawled

        Returns:
            None

        """
        for headline_number_block in headline_number_blocks:
            self.process_any_headline_number_block(
                headline_number_block=headline_number_block
            )

    def process_all_chart_blocks(
        self, *, chart_blocks: list[CMS_COMPONENT_BLOCK_TYPE]
    ) -> None:
        """Makes the relevant requests for the given `chart_blocks`

        Notes:
            This will handle the requests only for the chart elements.
            This will not include any headline number elements,
            which are located within the chart card

        Args:
            chart_blocks: List of all chart blocks on the page
                which are to be crawled

        Returns:
            None

        """
        for chart_block in chart_blocks:
            self.process_chart_block(chart_block=chart_block)

    # Process individual blocks

    def process_any_headline_number_block(
        self, *, headline_number_block: CMS_COMPONENT_BLOCK_TYPE
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

    def process_chart_block(self, *, chart_block: CMS_COMPONENT_BLOCK_TYPE) -> None:
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
        self._process_table_for_chart_block(chart_block=chart_block)
        self._process_chart_for_both_possible_widths(chart_block=chart_block)

    def process_all_global_filters(self, *, global_filters: list) -> None:
        """Makes the relevant requests for each of the given `global_filters`

        Notes:
            This will handle the requests for the maps API
            which are dictated by these `global_filters`.

        Args:
            global_filters: The global filter CMS blocks.

        Returns:
            None

        """
        for global_filter in global_filters:
            self.process_global_filter(global_filter=global_filter)

    def process_global_filter(self, *, global_filter: CMS_COMPONENT_BLOCK_TYPE) -> None:
        """Makes the relevant requests for the given single `global_filter`

        Notes:
            This will handle the requests for the maps API
            which are dictated by this `global_filter`.

        Args:
            global_filter: The global filter CMS block.

        Returns:
            None

        """
        self._process_global_filter_linked_maps(global_filter=global_filter)

    def _process_global_filter_linked_maps(
        self, *, global_filter: CMS_COMPONENT_BLOCK_TYPE
    ) -> None:
        payloads = self._extract_maps_payloads_for_global_filter(
            global_filter=global_filter
        )
        for payload in payloads:
            self._internal_api_client.hit_maps_endpoint(data=payload)

    @classmethod
    def _extract_maps_payloads_for_global_filter(cls, global_filter):
        block_parser = GlobalFilterCMSBlockParser(global_filter=global_filter)
        return block_parser.build_complete_payloads_for_maps_api()

    # Sub methods for processing charts

    def _process_table_for_chart_block(self, *, chart_block: dict):
        tables_data = self._request_payload_builder.build_tables_request_data(
            chart_block=chart_block
        )
        self._internal_api_client.hit_tables_endpoint(data=tables_data)

    def process_download_for_chart_block(self, *, chart_block: dict, file_format: str):
        downloads_data = self._request_payload_builder.build_downloads_request_data(
            chart_block=chart_block, file_format=file_format
        )
        return self._internal_api_client.hit_downloads_endpoint(data=downloads_data)

    def _process_chart_for_both_possible_widths(
        self, *, chart_block: CMS_COMPONENT_BLOCK_TYPE
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
                chart_block=chart_block,
                chart_is_double_width=chart_is_double_width,
            )
            self._internal_api_client.hit_charts_endpoint(data=charts_data)

    # Sub methods for processing headline number blocks

    def process_headline_number_block(
        self, *, headline_number_block: CMS_COMPONENT_BLOCK_TYPE
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
        self, *, trend_number_block: CMS_COMPONENT_BLOCK_TYPE
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
