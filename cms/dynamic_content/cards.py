from django.db import models
from wagtail import blocks

from cms.dashboard.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.dynamic_content import help_texts
from cms.dynamic_content.blocks import (
    HeadlineNumberBlockTypes,
    MetricNumberBlock,
    PageLinkChooserBlock,
    RelatedLinkBlock,
)
from cms.dynamic_content.components import (
    ChartComponent,
    HeadlineChartComponent,
    SimplifiedChartComponent,
)
from cms.metrics_interface.field_choices_callables import get_possible_axis_choices

MINIMUM_HEADLINE_COLUMNS_COUNT: int = 1
MAXIMUM_HEADLINE_COLUMNS_COUNT: int = 5

MINIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT: int = 0
MAXIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT: int = 2

MINIMUM_COLUMNS_CHART_COLUMNS_COUNT: int = 1
MAXIMUM_COLUMNS_CHART_COLUMNS_COUNT: int = 2
MAXIMUM_COLUMNS_CHART_THREE_COLUMNS_COUNT: int = 3

MAXIMUM_TOPIC_TREND_CARD_CHARTS: int = 1
MAXIMUM_TREND_NUMBER: int = 1

DEFAULT_SIMPLE_CHART_X_AXIS = "date"
DEFAULT_SIMPLE_CHART_Y_AXIS = "metric"

CHART_CARD_DATE_PREFIX_DEFAULT_TEXT = "Up to and including"


class TextCard(blocks.StructBlock):
    body = blocks.RichTextBlock(
        features=AVAILABLE_RICH_TEXT_FEATURES, help_text=help_texts.TEXT_CARD
    )

    class Meta:
        icon = "text"


class WHAlerts(models.TextChoices):
    HEAT = "heat"
    COLD = "cold"

    @classmethod
    def get_alerts(cls) -> tuple[tuple[str, str]]:
        return tuple((alert.value, alert.value) for alert in cls)


class WeatherHealthAlertsCard(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD)
    sub_title = blocks.TextBlock(required=True, help_text=help_texts.SUB_TITLE_FIELD)
    alert_type = blocks.ChoiceBlock(
        required=True,
        choices=WHAlerts.get_alerts,
        help_text=help_texts.WHA_ALERT_CHOICE,
    )

    class Meta:
        icon = "weather"


class HeadlineNumbersRowCard(blocks.StructBlock):
    columns = MetricNumberBlock(
        min_num=MINIMUM_HEADLINE_COLUMNS_COUNT,
        max_num=MAXIMUM_HEADLINE_COLUMNS_COUNT,
        help_text=help_texts.HEADLINE_COLUMNS_FIELD.format(
            MAXIMUM_HEADLINE_COLUMNS_COUNT
        ),
    )

    class Meta:
        icon = "headline_number"


class ChartWithHeadlineAndTrendCard(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD)
    body = blocks.TextBlock(required=False, help_text=help_texts.OPTIONAL_BODY_FIELD)
    related_links = RelatedLinkBlock(
        required=False, help_text=help_texts.OPTIONAL_RELATED_LINK
    )
    tag_manager_event_id = blocks.CharBlock(
        required=False,
        help_text=help_texts.TAG_MANAGER_EVENT_ID_FIELD,
        label="Tag manager event ID",
    )
    x_axis = blocks.ChoiceBlock(
        required=False,
        choices=get_possible_axis_choices,
        help_text=help_texts.CHART_X_AXIS,
    )
    x_axis_title = blocks.CharBlock(
        required=False,
        default="",
        help_text=help_texts.CHART_X_AXIS_TITLE,
    )
    y_axis = blocks.ChoiceBlock(
        required=False,
        choices=get_possible_axis_choices,
        help_text=help_texts.CHART_Y_AXIS,
    )
    y_axis_title = blocks.CharBlock(
        required=False,
        default="",
        help_text=help_texts.CHART_Y_AXIS_TITLE,
    )
    show_tooltips = blocks.BooleanBlock(
        help_text=help_texts.SHOW_TOOLTIPS_ON_CHARTS_FIELD,
        default=False,
        required=False,
    )
    date_prefix = blocks.CharBlock(
        required=True,
        default=CHART_CARD_DATE_PREFIX_DEFAULT_TEXT,
        help_text=help_texts.CHART_DATE_PREFIX,
    )
    chart = ChartComponent(help_text=help_texts.CHART_BLOCK_FIELD)
    headline_number_columns = HeadlineNumberBlockTypes(
        required=False,
        min_num=MINIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT,
        max_num=MAXIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT,
        help_text=help_texts.HEADLINE_COLUMNS_IN_CHART_CARD.format(
            MAXIMUM_HEADLINES_IN_CHART_CARD_COLUMN_COUNT
        ),
    )

    class Meta:
        icon = "chart_with_headline_and_trend_card"


class SimplifiedChartWithLink(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD)
    sub_title = blocks.CharBlock(required=False, help_text=help_texts.SUB_TITLE_FIELD)
    tag_manager_event_id = blocks.CharBlock(
        required=False,
        help_text=help_texts.TAG_MANAGER_EVENT_ID_FIELD,
        label="Tag manager event ID",
    )
    topic_page = PageLinkChooserBlock(
        page_type="topic.TopicPage",
        required=True,
        help_text=help_texts.TOPIC_PAGE_FIELD,
    )
    x_axis = blocks.ChoiceBlock(
        required=True,
        choices=get_possible_axis_choices,
        help_text=help_texts.REQUIRED_CHART_X_AXIS,
        default=DEFAULT_SIMPLE_CHART_X_AXIS,
        ready_only=True,
    )
    x_axis_title = blocks.CharBlock(
        required=False,
        default="",
        help_text=help_texts.CHART_X_AXIS_TITLE,
    )
    y_axis = blocks.ChoiceBlock(
        required=True,
        choices=get_possible_axis_choices,
        help_text=help_texts.REQUIRED_CHART_Y_AXIS,
        default=DEFAULT_SIMPLE_CHART_Y_AXIS,
    )
    y_axis_title = blocks.CharBlock(
        required=False,
        default="",
        help_text=help_texts.CHART_Y_AXIS_TITLE,
    )
    y_axis_minimum_value = blocks.DecimalBlock(
        required=False,
        default=0,
        help_text=help_texts.CHART_Y_AXIS_MINIMUM_VALUE,
    )
    y_axis_maximum_value = blocks.DecimalBlock(
        required=False,
        help_text=help_texts.CHART_Y_AXIS_MAXIMUM_VALUE,
    )
    chart = SimplifiedChartComponent(
        help_text=help_texts.CHART_BLOCK_FIELD,
        required=True,
        max_num=MAXIMUM_TOPIC_TREND_CARD_CHARTS,
    )

    class Meta:
        icon = "standalone_chart"


class ChartCard(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD)
    body = blocks.TextBlock(required=False, help_text=help_texts.OPTIONAL_BODY_FIELD)
    related_links = RelatedLinkBlock(
        required=False, help_text=help_texts.OPTIONAL_RELATED_LINK
    )
    tag_manager_event_id = blocks.CharBlock(
        required=False,
        help_text=help_texts.TAG_MANAGER_EVENT_ID_FIELD,
        label="Tag manager event ID",
    )
    x_axis = blocks.ChoiceBlock(
        required=False,
        choices=get_possible_axis_choices,
        help_text=help_texts.CHART_X_AXIS,
    )
    x_axis_title = blocks.CharBlock(
        required=False,
        default="",
        help_text=help_texts.CHART_X_AXIS_TITLE,
    )
    y_axis = blocks.ChoiceBlock(
        required=False,
        choices=get_possible_axis_choices,
        help_text=help_texts.CHART_Y_AXIS,
    )
    y_axis_title = blocks.CharBlock(
        required=False,
        default="",
        help_text=help_texts.CHART_Y_AXIS_TITLE,
    )
    show_tooltips = blocks.BooleanBlock(
        help_text=help_texts.SHOW_TOOLTIPS_ON_CHARTS_FIELD,
        default=False,
        required=False,
    )
    date_prefix = blocks.CharBlock(
        required=True,
        default=CHART_CARD_DATE_PREFIX_DEFAULT_TEXT,
        help_text=help_texts.CHART_DATE_PREFIX,
    )
    chart = ChartComponent(help_text=help_texts.CHART_BLOCK_FIELD)

    class Meta:
        icon = "standalone_chart"


class HeadlineChartCard(ChartCard):
    x_axis = blocks.ChoiceBlock(
        required=True,
        choices=get_possible_axis_choices,
        help_text=help_texts.REQUIRED_CHART_X_AXIS,
    )
    x_axis_title = blocks.CharBlock(
        required=False,
        default="",
        help_text=help_texts.CHART_X_AXIS_TITLE,
    )
    y_axis_title = blocks.CharBlock(
        required=False,
        default="",
        help_text=help_texts.CHART_Y_AXIS_TITLE,
    )
    show_tooltips = blocks.BooleanBlock(
        help_text=help_texts.SHOW_TOOLTIPS_ON_CHARTS_FIELD,
        default=False,
        required=False,
    )
    chart = HeadlineChartComponent(help_texts=help_texts.CHART_BLOCK_FIELD)

    class Meta:
        icon = "standalone_chart"


class ChartRowBlockTypes(blocks.StreamBlock):
    chart_card = ChartCard()
    headline_chart_card = HeadlineChartCard()
    chart_with_headline_and_trend_card = ChartWithHeadlineAndTrendCard()
    simplified_chart_with_link = SimplifiedChartWithLink()


class ChartRowCard(blocks.StructBlock):
    columns = ChartRowBlockTypes(
        min_num=MINIMUM_COLUMNS_CHART_COLUMNS_COUNT,
        max_num=MAXIMUM_COLUMNS_CHART_COLUMNS_COUNT,
        help_text=help_texts.CHART_CARD_ROW,
    )

    class Meta:
        icon = "chart_row_card"


class ChartCardSection(blocks.StructBlock):

    cards = ChartRowBlockTypes(
        min_num=MINIMUM_COLUMNS_CHART_COLUMNS_COUNT,
        help_text=help_texts.CHART_ROW_CARD_COLUMN_WIDTH_THREE,
    )

    class Meta:
        icon = "chart_row_card"
