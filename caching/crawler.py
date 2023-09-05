from typing import Optional

from caching.internal_api_client import InternalAPIClient
from cms.home.models import HomePage
from cms.topic.models import TopicPage

CMS_COMPONENT_BLOCK_TYPE = dict[str, str | dict[str, str] | list[dict[str, str]]]


class Crawler:
    def __init__(self, internal_api_client: Optional[InternalAPIClient] = None):
        self._internal_api_client = internal_api_client or InternalAPIClient()

    # Process sections

    def process_all_sections(self, page: HomePage | TopicPage) -> None:
        for section in page.body.raw_data:
            self.process_section(section=section)

    def process_section(self, section: dict[list[CMS_COMPONENT_BLOCK_TYPE]]) -> None:
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
                raise ValueError()

    def process_any_chart_card(self, chart_card: CMS_COMPONENT_BLOCK_TYPE) -> None:
        match chart_card["type"]:
            case "chart_card":
                self.process_chart_block(chart_block=chart_card)
            case "chart_with_headline_and_trend_card":
                self.process_chart_with_headline_and_trend_card(
                    chart_with_headline_and_trend_card=chart_card,
                )
            case _:
                raise ValueError()

    def process_chart_with_headline_and_trend_card(
        self,
        chart_with_headline_and_trend_card: CMS_COMPONENT_BLOCK_TYPE,
    ) -> None:
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
        chart_block_value = chart_block["value"]
        tables_data = self._build_tables_request_data(chart_block=chart_block_value)
        self._internal_api_client.hit_tables_endpoint(data=tables_data)

        self._process_chart_for_both_possible_widths(chart_block=chart_block)

    def _process_chart_for_both_possible_widths(
        self, chart_block: CMS_COMPONENT_BLOCK_TYPE
    ) -> None:
        for chart_is_double_width in (True, False):
            charts_data = self._build_chart_request_data(
                chart_block=chart_block["value"],
                chart_is_double_width=chart_is_double_width,
            )
            self._internal_api_client.hit_charts_endpoint(data=charts_data)

    def process_headline_number_block(
        self, headline_number_block: CMS_COMPONENT_BLOCK_TYPE
    ) -> None:
        data = self._build_headlines_request_data(
            headline_number_block=headline_number_block["value"]
        )
        self._internal_api_client.hit_headlines_endpoint(data=data)

    def process_trend_number_block(
        self, trend_number_block: CMS_COMPONENT_BLOCK_TYPE
    ) -> None:
        data = self._build_trend_request_data(
            trend_number_block=trend_number_block["value"]
        )
        self._internal_api_client.hit_trends_endpoint(data=data)

    # Deconstruct blocks

    @staticmethod
    def get_content_cards_from_section(
        section: dict[list[CMS_COMPONENT_BLOCK_TYPE]],
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        return section["value"]["content"]

    @staticmethod
    def get_chart_row_cards_from_content_cards(
        content_cards: list[CMS_COMPONENT_BLOCK_TYPE],
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        return [
            content_card
            for content_card in content_cards
            if content_card["type"] == "chart_row_card"
        ]

    @staticmethod
    def get_headline_numbers_row_cards_from_content_cards(
        content_cards: list[CMS_COMPONENT_BLOCK_TYPE],
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        return [
            content_card
            for content_card in content_cards
            if content_card["type"] == "headline_numbers_row_card"
        ]

    # Building request data

    @staticmethod
    def _build_headlines_request_data(headline_number_block) -> dict[str, str]:
        return {
            "topic": headline_number_block["topic"],
            "metric": headline_number_block["metric"],
            "geography": headline_number_block.get("geography", "England"),
            "geography_type": headline_number_block.get("geography_type", "Nation"),
        }

    @staticmethod
    def _build_trend_request_data(trend_number_block: dict[str, str]) -> dict[str, str]:
        return {
            "topic": trend_number_block["topic"],
            "metric": trend_number_block["metric"],
            "percentage_metric": trend_number_block["percentage_metric"],
        }

    def _build_chart_request_data(
        self, chart_block: CMS_COMPONENT_BLOCK_TYPE, chart_is_double_width: bool
    ) -> dict[str, str | int, list[dict[str, str]]]:
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
        return {
            "topic": plot_value["topic"],
            "metric": plot_value["metric"],
            "chart_type": plot_value["chart_type"],
            "date_from": plot_value["date_from"],
            "date_to": plot_value["date_to"],
            "stratum": plot_value["stratum"],
            "geography": plot_value["geography"],
            "geography_type": plot_value["geography_type"],
            "sex": plot_value["sex"],
            "label": plot_value["label"],
            "line_colour": plot_value["line_colour"],
            "line_type": plot_value["line_type"],
        }

    def _build_tables_request_data(
        self, chart_block: CMS_COMPONENT_BLOCK_TYPE
    ) -> dict[str, str | int, list[dict[str, str]]]:
        return {
            "plots": [
                self._build_plot_data(plot_value=plot["value"])
                for plot in chart_block["chart"]
            ],
        }
