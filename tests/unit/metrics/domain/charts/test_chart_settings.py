import datetime
from unittest import mock

import pytest

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings import ChartSettings
from metrics.domain.models import PlotParameters, PlotsData


@pytest.fixture
def fake_chart_plots_data() -> PlotsData:
    plot_params = PlotParameters(
        chart_type="line_multi_coloured",
        topic="COVID-19",
        metric="new_cases_daily",
    )
    x_values = [1, 2, 4, 5, 5, 2, 1]
    return PlotsData(
        parameters=plot_params,
        x_axis_values=[1, 2, 4, 5, 5, 2, 1],
        y_axis_values=[
            datetime.date(year=2023, month=1, day=i + 1) for i in range(len(x_values))
        ],
    )


@pytest.fixture()
def fake_chart_settings(fake_chart_plots_data: PlotsData) -> ChartSettings:
    return ChartSettings(
        width=930,
        height=220,
        plots_data=fake_chart_plots_data,
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

    def test_get_x_axes_setting(self, fake_chart_settings: ChartSettings):
        """
        Given an instance of `ChartSettings`
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

    def test_get_simple_line_chart_config(self, fake_chart_settings: ChartSettings):
        """
        Given an instance of `ChartSettings`
        When `_get_simple_line_chart_config()` is called
        Then the correct configuration for simple line charts is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        simple_line_chart_config = chart_settings._get_simple_line_chart_config()

        # Then
        expected_line_chart_config = {
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
            "plot_bgcolor": colour_scheme.RGBAColours.LINE_LIGHT_GREY.stringified,
        }
        assert simple_line_chart_config == expected_line_chart_config

    def test_chart_settings_width(self, fake_chart_plots_data: PlotsData):
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
            plots_data=fake_chart_plots_data,
        )

        # When
        chart_width: int = chart_settings.width

        # Then
        assert chart_width == width

    def test_chart_settings_height(self, fake_chart_plots_data: PlotsData):
        """
        Given a `width` integer
        When the `width` property is called from an instance of `ChartSettings`
        Then the correct number is returned
        """
        # Given
        height = 220
        chart_settings = ChartSettings(
            width=930, height=height, plots_data=fake_chart_plots_data
        )

        # When
        chart_height: int = chart_settings.height

        # Then
        assert chart_height == height

    def test_waffle_chart_config(self, fake_chart_plots_data: PlotsData):
        """
        Given an instance of `ChartSettings`
        When `_get_waffle_chart_config()` is called
        Then the correct configuration for waffle charts is returned as a dict
        """
        # Given
        width = height = 400
        chart_settings = ChartSettings(
            width=width, height=height, plots_data=fake_chart_plots_data
        )

        # When
        waffle_chart_config = chart_settings._get_waffle_chart_config()

        # Then
        x_axis_args = {
            "showgrid": False,
            "ticks": None,
            "showticklabels": False,
        }
        y_axis_args = {**x_axis_args, **{"scaleratio": 1, "scaleanchor": "x"}}
        expected_chart_config = {
            "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
            "showlegend": False,
            "plot_bgcolor": colour_scheme.RGBAColours.LIGHT_GREY.stringified,
            "paper_bgcolor": colour_scheme.RGBAColours.WAFFLE_WHITE.stringified,
            "xaxis": x_axis_args,
            "yaxis": y_axis_args,
            "width": width,
            "height": height,
        }
        assert waffle_chart_config == expected_chart_config

    def test_chart_settings_can_determine_x_axis_data_type(self, fake_chart_settings):
        """
        Given
        When
        Then
        """
        # Given
        fake_chart_settings

        # When

        # Then
