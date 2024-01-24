from unittest import mock

import pytest

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings import ChartSettings, get_new_max_date
from metrics.domain.models import PlotData

MODULE_PATH: str = "metrics.domain.charts.chart_settings"


@pytest.fixture()
def fake_chart_settings(fake_plot_data: PlotData) -> ChartSettings:
    return ChartSettings(
        width=930,
        height=220,
        plots_data=[fake_plot_data],
    )


class TestChartSettings:
    def test_get_tick_font_setting(self, fake_chart_settings: ChartSettings):
        """
        Given an instance of `ChartSettings`
        When `get_tick_font_config()` is called
        Then the correct tick font configuration is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        tick_font_config = chart_settings.get_tick_font_config()

        # Then
        expected_tick_font_config = {
            "family": "Arial",
            "color": colour_scheme.RGBAColours.DARK_BLUE_GREY.stringified,
        }
        assert tick_font_config == expected_tick_font_config

    def test_get_x_axes_setting_for_date_based_x_axis(
        self, fake_chart_settings: ChartSettings
    ):
        """
        Given an instance of `ChartSettings`
            with date-based x axes values
        When `get_x_axis_config()` is called
        Then the correct X axis configuration is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        x_axis_config = chart_settings.get_x_axis_config()

        # Then
        expected_x_axis_config = {
            "showgrid": False,
            "zeroline": False,
            "showline": False,
            "ticks": "outside",
            "tickson": "boundaries",
            "type": "date",
            "dtick": "M1",
            "tickformat": "%b %Y",
            "tickfont": chart_settings.get_tick_font_config(),
        }
        expected_x_axis_config = {
            **expected_x_axis_config,
            **chart_settings.get_x_axis_date_type(),
        }
        assert x_axis_config == expected_x_axis_config

    def test_get_x_axes_setting_for_text_based_x_axis(
        self, fake_chart_settings: ChartSettings
    ):
        """
        Given an instance of `ChartSettings`
            with text-based x axes values
        When `get_x_axis_config()` is called
        Then the correct X axis configuration is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings
        original_values = chart_settings.plots_data[0].x_axis_values
        chart_settings.plots_data[0].x_axis_values = [
            f"P-{i}" for i in range(len(original_values))
        ]

        # When
        x_axis_config = chart_settings.get_x_axis_config()

        # Then
        expected_x_axis_config = {
            "showgrid": False,
            "zeroline": False,
            "showline": False,
            "ticks": "outside",
            "tickson": "boundaries",
            "type": "-",
            "dtick": None,
            "tickformat": None,
            "tickfont": chart_settings.get_tick_font_config(),
        }
        assert x_axis_config == expected_x_axis_config

    def test_get_y_axes_setting(self, fake_chart_settings: ChartSettings):
        """
        Given an instance of `ChartSettings`
        When `get_y_axis_config()` is called
        Then the correct Y axis configuration is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        y_axis_config = chart_settings.get_y_axis_config()

        # Then
        expected_y_axis_config = {
            "showgrid": False,
            "showticklabels": True,
            "tickfont": chart_settings.get_tick_font_config(),
        }
        assert y_axis_config == expected_y_axis_config

    @mock.patch.object(ChartSettings, "get_y_axis_config")
    @mock.patch.object(ChartSettings, "get_x_axis_config")
    def test_get_base_chart_config(
        self,
        mocked_get_x_axis_config: mock.MagicMock,
        mocked_get_y_axis_config: mock.MagicMock,
        fake_chart_settings: ChartSettings,
    ):
        """
        Given an instance of `ChartSettings`
        When `get_base_chart_config()` is called
        Then the correct base chart configuration is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        base_chart_config = chart_settings.get_base_chart_config()

        # Then
        expected_base_chart_config = {
            "paper_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
            "plot_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
            "margin": {
                "l": 15,  # Margin expected for date-based x-axes
                "r": 15,
                "b": 0,
                "t": 0,
            },
            "autosize": False,
            "xaxis": mocked_get_x_axis_config.return_value,
            "yaxis": mocked_get_y_axis_config.return_value,
            "width": chart_settings.width,
            "height": chart_settings.height,
        }

        assert base_chart_config == expected_base_chart_config

    def test_chart_settings_width(self, fake_plot_data: PlotData):
        """
        Given a `width` integer
        When the `width` property is called from an instance of `ChartSettings`
        Then the correct number is returned
        """
        # Given
        width = 930
        chart_settings = ChartSettings(
            width=width,
            height=220,
            plots_data=[fake_plot_data],
        )

        # When
        chart_width: int = chart_settings.width

        # Then
        assert chart_width == width

    def test_chart_settings_height(self, fake_plot_data: PlotData):
        """
        Given a `width` integer
        When the `width` property is called from an instance of `ChartSettings`
        Then the correct number is returned
        """
        # Given
        height = 220
        chart_settings = ChartSettings(
            width=930, height=height, plots_data=[fake_plot_data]
        )

        # When
        chart_height: int = chart_settings.height

        # Then
        assert chart_height == height

    def test_get_x_axis_date_type(self, fake_chart_settings: ChartSettings):
        """
        Given an instance of `ChartSettings`
        When `get_x_axis_date_type()` is called
        Then the correct configuration for the x-axis is returned as a dict

        Patches:
            `mocked_get_x_axis_range`: To remove the need
                 to supply a valid plotly figure object to the test
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        x_axis_date_type = chart_settings.get_x_axis_date_type()

        # Then
        assert x_axis_date_type["type"] == "date"
        assert x_axis_date_type["dtick"] == "M1"
        assert x_axis_date_type["tickformat"] == "%b %Y"

    def test_get_x_axis_date_type_calls_get_x_axis_range(
        self, fake_plot_data: PlotData
    ):
        """
        Given an instance of `ChartSettings`
        When `get_x_axis_date_type()` is called
        Then the correct config is returned
        """
        # Given
        chart_settings = ChartSettings(
            width=435, height=220, plots_data=[fake_plot_data]
        )

        # When
        x_axis_date_type = chart_settings.get_x_axis_date_type()

        # Then
        min_date, _ = chart_settings.get_min_and_max_x_axis_values()
        month_end_of_max_date = "2023-01-31"

        expected_axis_config = {
            "type": "date",
            "dtick": "M1",
            "tickformat": "%b<br>%Y",
            "range": [min_date, month_end_of_max_date],
        }
        assert x_axis_date_type == expected_axis_config

    def test_get_x_axis_date_type_breaks_line_for_narrow_charts(
        self, fake_plot_data: PlotData
    ):
        """
        Given an instance of `ChartSettings` with a narrow `width`
        When `get_x_axis_date_type()` is called
        Then the correct configuration for the x-axis is returned as a dict
        """
        # Given
        chart_settings = ChartSettings(
            width=435, height=220, plots_data=[fake_plot_data]
        )

        # When
        x_axis_date_type = chart_settings.get_x_axis_date_type()

        # Then
        assert x_axis_date_type["tickformat"] == "%b<br>%Y"

    def test_get_x_axis_text_type(self, fake_chart_settings: ChartSettings):
        """
        Given an instance of `ChartSettings`
        When `get_x_axis_text_type()` is called
        Then the correct configuration for the x-axis is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        x_axis_text_type = chart_settings.get_x_axis_text_type()

        # Then
        expected_axis_config = {
            "type": "-",
            "dtick": None,
            "tickformat": None,
        }
        assert x_axis_text_type == expected_axis_config

    def test_get_line_with_shaded_section_chart_config(
        self, fake_chart_settings: ChartSettings
    ):
        """
        Given an instance of `ChartSettings`
        When `get_line_with_shaded_section_chart_config()` is called
        Then the correct configuration for
            `line_with_shaded_section` charts is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        line_with_shaded_section_chart_config = (
            chart_settings.get_line_with_shaded_section_chart_config()
        )

        # Then
        expected_chart_config = chart_settings.get_base_chart_config()
        expected_chart_config["showlegend"] = False

        assert line_with_shaded_section_chart_config == expected_chart_config

    def test_get_margin_for_charts_with_dates(self, fake_chart_settings: ChartSettings):
        """
        Given an instance of `ChartSettings`
        When `get_margin_for_charts_with_dates()` is called
        Then the correct configuration for margins is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        margin_config = chart_settings.get_margin_for_charts_with_dates()

        # Then
        expected_margin_config = {
            "margin": {
                "l": 15,
                "r": 15,
                "b": 0,
                "t": 0,
            }
        }
        assert margin_config == expected_margin_config

    def test_get_bar_chart_config(self, fake_chart_settings: ChartSettings):
        """
        Given an instance of `ChartSettings`
        When `get_bar_chart_config()` is called
        Then the correct configuration for margins is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        bar_chart_config = chart_settings.get_bar_chart_config()

        # Then
        additional_bar_chart_specific_config = {
            "barmode": "group",
            "legend": {
                "orientation": "h",
                "y": -0.25,
                "x": 0,
            },
        }
        expected_bar_chart_config = {
            **chart_settings.get_base_chart_config(),
            **additional_bar_chart_specific_config,
        }
        assert bar_chart_config == expected_bar_chart_config

    def test_get_legend_bottom_left_config(self, fake_chart_settings: ChartSettings):
        """
        Given an instance of `ChartSettings`
        When `_get_legend_bottom_left_config()` is called
        Then the correct configuration for the legend is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        legend_bottom_left_config = chart_settings._get_legend_bottom_left_config()

        # Then
        expected_legend_bottom_left_config = {
            "legend": {
                "orientation": "h",
                "y": -0.25,
                "x": 0,
            },
        }
        assert legend_bottom_left_config == expected_legend_bottom_left_config

    def test_get_legend_top_centre_config(self, fake_chart_settings: ChartSettings):
        """
        Given an instance of `ChartSettings`
        When `_get_legend_top_centre_config()` is called
        Then the correct configuration for the legend is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        legend_top_centre_config = chart_settings._get_legend_top_centre_config()

        # Then
        expected_legend_top_centre_config = {
            "legend": {
                "orientation": "h",
                "y": 1.0,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "bottom",
            },
        }
        assert legend_top_centre_config == expected_legend_top_centre_config

    @mock.patch(f"{MODULE_PATH}.is_legend_required")
    def test_get_line_multi_coloured_chart_config(
        self, spy_is_legend_required: mock.MagicMock, fake_chart_settings: ChartSettings
    ):
        """
        Given an instance of `ChartSettings`
        When `get_line_multi_coloured_chart_config()` is called
        Then the correct configuration for margins is returned as a dict

        Patches:
            `spy_is_legend_required`: To check if the call is delegated
                correctly to determine if a legend is needed.
                Which is based on whether any `labels` were requested
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        line_multi_coloured_chart_config = (
            chart_settings.get_line_multi_coloured_chart_config()
        )

        # Then
        spy_is_legend_required.assert_called_once_with(
            chart_plots_data=chart_settings.plots_data
        )
        expected_line_multi_coloured_chart_config = {
            **chart_settings.get_base_chart_config(),
            **chart_settings._get_legend_top_centre_config(),
            "showlegend": spy_is_legend_required.return_value,
        }
        assert (
            line_multi_coloured_chart_config
            == expected_line_multi_coloured_chart_config
        )

    @pytest.mark.parametrize(
        "chart_width, expected_date_tick_format", ([430, "%b<br>%Y"], [930, "%b %Y"])
    )
    def test_get_date_tick_format(
        self,
        chart_width: int,
        expected_date_tick_format: str,
        fake_chart_settings: ChartSettings,
    ):
        """
        Given an instance of `ChartSettings`
        When `_get_date_tick_format()` is called
        Then the correct string is returned
        """
        # Given
        fake_chart_settings._width = chart_width

        # When
        returned_date_tick_format: str = fake_chart_settings._get_date_tick_format()

        # Then
        assert returned_date_tick_format == expected_date_tick_format

    def test_get_min_and_max_x_axis_values(self, fake_chart_settings: ChartSettings):
        """
        Given an instance of `ChartSettings`
        When `get_min_and_max_x_axis_values()` is called
        Then the correct dates are returned
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        min_date, max_date = chart_settings.get_min_and_max_x_axis_values()

        # Then
        assert min_date == chart_settings.plots_data[0].x_axis_values[0]
        assert max_date == chart_settings.plots_data[0].x_axis_values[-1]


class TestGetNewMaxDate:
    def test_get_new_max_date(self):
        """
        Given a date as a string
        When `get_new_max_date()` is called
        Then the end of the month date is returned as a string
        """
        # Given
        input_date = "2024-02-15 12:00"
        expected_date = "2024-02-29"

        # When
        actual_date = get_new_max_date(input_date)

        # Then
        assert expected_date == actual_date

    def test_date_is_already_the_last_day(self):
        """
        Given a date as a string that is the end of the month
        When `get_new_max_date()` is called
        Then the same date is returned
        """
        # Given
        input_date = "2024-02-29 12:00"
        expected_date = "2024-02-29"

        # When
        actual_date = get_new_max_date(input_date)

        # Then
        assert expected_date == actual_date
