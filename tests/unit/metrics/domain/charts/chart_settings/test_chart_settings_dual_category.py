import pytest

from metrics.domain.charts.chart_settings.dual_category import DualCategoryChartSettings
from metrics.domain.models import ChartGenerationPayload, PlotGenerationData
from tests.conftest import fake_plot_data


@pytest.fixture()
def fake_dual_category_chart_settings(
    fake_plot_data: PlotGenerationData,
) -> DualCategoryChartSettings:
    payload = ChartGenerationPayload(
        chart_width=640,
        chart_height=400,
        plots=[fake_plot_data],
        x_axis_title="Date",
        y_axis_title="Cases",
    )
    return DualCategoryChartSettings(chart_generation_payload=payload)


class TestDualCategoryChartSettings:
    def test_get_legend_config(
        self, fake_dual_category_chart_settings: DualCategoryChartSettings
    ):
        """
        Given an instance of `DualCategoryChartSettings` without a legend title
        When `_get_legend_config()` is called
        Then the legend configuration is returned without a title
        """
        # Given
        chart_settings = fake_dual_category_chart_settings

        # When
        legend_config = chart_settings._get_legend_config()

        # Then
        assert legend_config == {
            "legend": {
                "font": chart_settings._get_tick_font_config(),
                "orientation": "h",
                "y": 1.0,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "bottom",
                "entrywidth": 80,
            },
        }

    def test_get_legend_config_includes_legend_title_when_provided(
        self, fake_dual_category_chart_settings: DualCategoryChartSettings
    ):
        """
        Given an instance of `DualCategoryChartSettings` with a legend title
        When `_get_legend_config()` is called
        Then the legend configuration includes a formatted title
        """
        # Given
        chart_settings = fake_dual_category_chart_settings
        legend_title = "Age group"
        chart_settings._chart_generation_payload.legend_title = legend_title

        # When
        legend_config = chart_settings._get_legend_config()

        # Then
        assert legend_config == {
            "legend": {
                "font": chart_settings._get_tick_font_config(),
                "orientation": "h",
                "y": 1.0,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "bottom",
                "entrywidth": 80,
                "title": {
                    "text": f"<b>{legend_title}</b>",
                    "side": "top",
                },
            },
        }

    def test_get_stacked_bar_chart_config(
        self, fake_dual_category_chart_settings: DualCategoryChartSettings
    ):
        """
        Given an instance of `DualCategoryChartSettings`
        When `get_stacked_bar_chart_config()` is called
        Then stacked bar layout and legend settings are merged
        """
        # Given
        chart_settings = fake_dual_category_chart_settings

        # When
        stacked_bar_config = chart_settings.get_stacked_bar_chart_config()

        expected_config = {
            **chart_settings._get_base_chart_config(),
            **chart_settings._get_legend_config(),
            "barmode": "stack",
        }

        # Then
        assert stacked_bar_config == expected_config
