import pytest

from caching.common.chart_block import is_dual_category_chart_block


def _build_dual_category_chart_block(*, chart_type: str) -> dict:
    return {
        "title": "Cases by age and sex",
        "x_axis": "age",
        "y_axis": "metric",
        "chart_type": chart_type,
        "primary_field_values": ["00-04", "05-11"],
        "secondary_category": "sex",
        "segments": [
            {"secondary_field_value": "m", "colour": "COLOUR_1_DARK_BLUE"},
            {"secondary_field_value": "f", "colour": "COLOUR_4_ORANGE"},
        ],
    }


class TestIsDualCategoryChartBlock:
    @pytest.mark.parametrize("chart_type", ("stacked_bar", "butterfly"))
    def test_returns_true_for_supported_dual_category_chart_types(
        self, chart_type: str
    ):
        """
        Given a chart block for a supported dual category chart type
        When `is_dual_category_chart_block()` is called
        Then True is returned
        """
        # Given
        chart_block = _build_dual_category_chart_block(chart_type=chart_type)

        # When
        is_dual_category = is_dual_category_chart_block(chart_block)

        # Then
        assert is_dual_category

    def test_returns_false_for_single_category_chart_types(self):
        """
        Given a chart block for a single category chart type
        When `is_dual_category_chart_block()` is called
        Then False is returned
        """
        # Given
        chart_block = _build_dual_category_chart_block(chart_type="bar")

        # When
        is_dual_category = is_dual_category_chart_block(chart_block)

        # Then
        assert not is_dual_category

    def test_returns_false_when_segments_are_not_provided(self):
        """
        Given a dual category chart block which has no segments
        When `is_dual_category_chart_block()` is called
        Then False is returned
        """
        # Given
        chart_block = _build_dual_category_chart_block(chart_type="butterfly")
        chart_block.pop("segments")

        # When
        is_dual_category = is_dual_category_chart_block(chart_block)

        # Then
        assert not is_dual_category

    def test_returns_false_when_axes_fields_are_not_provided(self):
        """
        Given a dual category chart block which has no axes fields
        When `is_dual_category_chart_block()` is called
        Then False is returned
        """
        # Given
        chart_block = _build_dual_category_chart_block(chart_type="butterfly")
        chart_block.pop("x_axis")
        chart_block.pop("primary_field_values")

        # When
        is_dual_category = is_dual_category_chart_block(chart_block)

        # Then
        assert not is_dual_category
