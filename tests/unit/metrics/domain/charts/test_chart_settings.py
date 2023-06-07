from unittest import mock

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings import ChartSettings


class TestChartSettings:
    def test_get_tick_font_setting(self):
        """
        Given an instance of `ChartSettings`
        When `get_tick_font_config()` is called
        Then the correct tick font configuration is returned as a dict
        """
        # Given
        chart_settings = ChartSettings()

        # When
        tick_font_config = chart_settings.get_tick_font_config()

        # Then
        expected_tick_font_config = {
            "family": "Arial",
            "color": colour_scheme.RGBAColours.DARK_BLUE_GREY.stringified,
        }
        assert tick_font_config == expected_tick_font_config

    def test_get_x_axes_setting(self):
        """
        Given an instance of `ChartSettings`
        When `get_x_axis_config()` is called
        Then the correct X axis configuration is returned as a dict
        """
        # Given
        chart_settings = ChartSettings()

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
        assert x_axis_config == expected_x_axis_config

    def test_get_y_axes_setting(self):
        """
        Given an instance of `ChartSettings`
        When `get_y_axis_config()` is called
        Then the correct Y axis configuration is returned as a dict
        """
        # Given
        chart_settings = ChartSettings()

        # When
        y_axis_config = chart_settings.get_y_axis_config()

        # Then
        expected_y_axis_config = {
            "showgrid": False,
            "showticklabels": False,
            "tickfont": chart_settings.get_tick_font_config(),
        }
        assert y_axis_config == expected_y_axis_config

    @mock.patch.object(ChartSettings, "get_y_axis_config")
    @mock.patch.object(ChartSettings, "get_x_axis_config")
    def test_get_base_chart_config(
        self,
        mocked_get_x_axis_config: mock.MagicMock,
        mocked_get_y_axis_config: mock.MagicMock,
    ):
        """
        Given an instance of `ChartSettings`
        When `get_base_chart_config()` is called
        Then the correct base chart configuration is returned as a dict
        """
        # Given
        chart_settings = ChartSettings()

        # When
        base_chart_config = chart_settings.get_base_chart_config()

        # Then
        expected_base_chart_config = {
            "paper_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
            "plot_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
            "margin": {
                "l": 0,
                "r": 0,
                "b": 0,
                "t": 0,
            },
            "autosize": False,
            "xaxis": mocked_get_x_axis_config.return_value,
            "yaxis": mocked_get_y_axis_config.return_value,
        }

        assert base_chart_config == expected_base_chart_config
