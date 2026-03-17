import pytest

from cms.dynamic_content.blocks import (
    POPULAR_TOPICS_BOTTOM_RIGHT_COLUMN_COUNT,
    POPULAR_TOPICS_HEADLINE_NUMBER_BLOCK_COUNT,
    PopularTopicsMetricNumberBlockTypes,
    PopularTopicsRightColumnBottomRowBlockTypes,
)
from cms.dynamic_content.cards import (
    POPULAR_TOPICS_RIGHT_COLUMN_BOTTOM_ROW_SEGMENT_COUNT,
    PopularTopicsCard,
    PopularTopicsLeftColumnBlockTypes,
    PopularTopicsRightColumnTopRowBlockTypes,
    SimplifiedChartWithLink,
)


class TestPopularTopicsFirstColumnBlockTypes:
    @pytest.mark.parametrize(
        "expected_field_name",
        (
            "weather_health_alert_card",
            "chart_card_with_description",
        ),
    )
    def test_has_expected_child_blocks(self, expected_field_name: str) -> None:
        """
        Given an instance of `PopularTopicsLeftColumnBlockTypes`
        When inspecting child blocks
        Then the expected field(s) are available
        """
        # Given
        first_column_block_types = PopularTopicsLeftColumnBlockTypes()

        # When
        selected_field = first_column_block_types.child_blocks.get(expected_field_name)

        # Then
        assert selected_field is not None


class TestPopularTopicsSecondColumnTopRightBlockTypes:
    def test_has_expected_chart_card_block(self) -> None:
        """
        Given an instance of `PopularTopicsRightColumnTopRowBlockTypes`
        When inspecting child blocks
        Then the chart card field is available and correctly typed
        """
        # Given
        top_right_block_types = PopularTopicsRightColumnTopRowBlockTypes()

        # When
        selected_field = top_right_block_types.child_blocks.get("chart_card")

        # Then
        assert isinstance(selected_field, SimplifiedChartWithLink)


class TestPopularTopicsSecondColumnBottomRowBlockTypes:
    def test_has_expected_headline_metric_card_block(self) -> None:
        """
        Given an instance of `PopularTopicsRightColumnBottomRowBlockTypes`
        When inspecting child blocks
        Then the headline metric card field is available and correctly typed
        """
        # Given
        bottom_row_block_types = PopularTopicsRightColumnBottomRowBlockTypes()

        # When
        selected_field = bottom_row_block_types.child_blocks.get("headline_metric_card")

        # Then
        assert isinstance(selected_field, PopularTopicsMetricNumberBlockTypes)
        assert selected_field.meta.min_num == POPULAR_TOPICS_BOTTOM_RIGHT_COLUMN_COUNT
        assert selected_field.meta.max_num == POPULAR_TOPICS_BOTTOM_RIGHT_COLUMN_COUNT


class TestPopularTopicsCard:
    @pytest.mark.parametrize(
        "field_name, expected_block_type",
        (
            ("left_column", PopularTopicsLeftColumnBlockTypes),
            ("right_column_top_row", PopularTopicsRightColumnTopRowBlockTypes),
            ("right_column_bottom_row", PopularTopicsRightColumnBottomRowBlockTypes),
        ),
    )
    def test_has_expected_child_blocks(
        self,
        field_name: str,
        expected_block_type: type,
    ) -> None:
        """
        Given an instance of `PopularTopicsCard`
        When inspecting child blocks
        Then the expected field(s) use the correct block type
        """
        # Given
        popular_topics_card = PopularTopicsCard()

        # When
        selected_field = popular_topics_card.child_blocks.get(field_name)

        # Then
        assert isinstance(selected_field, expected_block_type)

    @pytest.mark.parametrize(
        "field_name, expected_min_num, expected_max_num",
        (
            ("left_column", 1, 1),
            ("right_column_top_row", 1, 1),
            (
                "right_column_bottom_row",
                POPULAR_TOPICS_RIGHT_COLUMN_BOTTOM_ROW_SEGMENT_COUNT,
                POPULAR_TOPICS_RIGHT_COLUMN_BOTTOM_ROW_SEGMENT_COUNT,
            ),
        ),
    )
    def test_card_columns_have_expected_required_counts(
        self,
        field_name: str,
        expected_min_num: int,
        expected_max_num: int,
    ) -> None:
        """
        Given an instance of `PopularTopicsCard`
        When inspecting stream count constraints for each card area
        Then each field has the expected min and max values
        """
        # Given
        popular_topics_card = PopularTopicsCard()

        # When
        selected_field = popular_topics_card.child_blocks[field_name]

        # Then
        assert selected_field.meta.min_num == expected_min_num
        assert selected_field.meta.max_num == expected_max_num


class TestPopularTopicsMetricNumberBlockTypes:
    def test_headline_metrics_are_required_and_allow_exactly_two_entries(self) -> None:
        """
        Given an instance of `PopularTopicsMetricNumberBlockTypes`
        When inspecting the headline_metrics field configuration
        Then headline_metrics are required and constrained to exactly two entries
        """
        # Given
        metric_number_block = PopularTopicsMetricNumberBlockTypes()

        # When
        headline_metrics_block = metric_number_block.child_blocks["headline_metrics"]

        # Then
        assert headline_metrics_block.meta.required is True
        assert (
            headline_metrics_block.meta.min_num
            == POPULAR_TOPICS_HEADLINE_NUMBER_BLOCK_COUNT
        )
        assert (
            headline_metrics_block.meta.max_num
            == POPULAR_TOPICS_HEADLINE_NUMBER_BLOCK_COUNT
        )
