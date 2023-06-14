import datetime
from unittest import mock

import pytest

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings import ChartSettings, get_new_max_date
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

    def test_get_x_axis_date_type(self, fake_chart_settings: ChartSettings):
        """
        Given an instance of `ChartSettings`
        When `_get_x_axis_date_type()` is called
        Then the correct configuration for the x-axis is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        x_axis_date_type = chart_settings._get_x_axis_date_type()

        # Then
        expected_axis_config = {
            "type": "date",
            "dtick": "M1",
            "tickformat": "%b %Y",
        }
        assert x_axis_date_type == expected_axis_config

    def test_get_x_axis_text_type(self, fake_chart_settings: ChartSettings):
        """
        Given an instance of `ChartSettings`
        When `_get_x_axis_text_type()` is called
        Then the correct configuration for the x-axis is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        x_axis_text_type = chart_settings._get_x_axis_text_type()

        # Then
        expected_axis_config = {
            "type": "-",
            "dtick": None,
            "tickformat": None,
        }
        assert x_axis_text_type == expected_axis_config


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
