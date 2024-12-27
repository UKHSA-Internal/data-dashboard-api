import datetime
from unittest import mock

import pytest

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings import (
    ChartSettings,
    get_max_date_for_current_month,
)
from metrics.domain.models import PlotGenerationData, ChartGenerationPayload

MODULE_PATH: str = "metrics.domain.charts.chart_settings"


@pytest.fixture()
def fake_chart_settings(fake_plot_data: PlotGenerationData) -> ChartSettings:
    payload = ChartGenerationPayload(
        chart_width=930,
        chart_height=220,
        plots=[fake_plot_data],
        x_axis_title="Date",
        y_axis_title="Cases",
    )
    return ChartSettings(chart_generation_payload=payload)


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
            "showspikes": True,
            "spikecolor": "#b1b4b6",
            "spikedash": "2px",
            "spikethickness": 1,
            "spikemode": "toaxis+across+marker",
            "spikesnap": "cursor",
            "showline": False,
            "fixedrange": True,
            "gridcolor": "rgba(0,0,0,0.05)",
            "tickcolor": "rgba(0,0,0,0)",
            "showgrid": True,
            "zeroline": False,
            "ticks": "outside",
            "tickson": "boundaries",
            "type": "date",
            "dtick": "M1",
            "tickformat": "%b %Y",
            "tickfont": chart_settings.get_tick_font_config(),
            "title": {
                "font": chart_settings.get_tick_font_config(),
                "text": chart_settings._chart_generation_payload.x_axis_title,
            },
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
            "showspikes": True,
            "spikecolor": "#b1b4b6",
            "spikedash": "2px",
            "spikethickness": 1,
            "spikemode": "toaxis+across+marker",
            "spikesnap": "cursor",
            "showline": False,
            "showgrid": True,
            "zeroline": False,
            "fixedrange": True,
            "gridcolor": "rgba(0,0,0,0.05)",
            "tickcolor": "rgba(0,0,0,0)",
            "ticks": "outside",
            "tickson": "boundaries",
            "type": "-",
            "dtick": None,
            "tickformat": None,
            "tickfont": chart_settings.get_tick_font_config(),
            "title": {
                "font": chart_settings.get_tick_font_config(),
                "text": chart_settings._chart_generation_payload.x_axis_title,
            },
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
            "rangemode": "tozero",
            "showgrid": False,
            "showticklabels": True,
            "fixedrange": True,
            "gridcolor": "#000",
            "ticks": "outside",
            "tickson": "boundaries",
            "tickcolor": "rgba(0,0,0,0)",
            "tickfont": chart_settings.get_tick_font_config(),
            "title": {
                "font": chart_settings.get_tick_font_config(),
                "text": chart_settings._chart_generation_payload.y_axis_title,
            },
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
            "hoverlabel": {
                "align": "left",
                "bgcolor": "white",
            },
            "autosize": False,
            "xaxis": mocked_get_x_axis_config.return_value,
            "yaxis": mocked_get_y_axis_config.return_value,
            "width": chart_settings.width,
            "height": chart_settings.height,
            "showlegend": True,
        }

        assert base_chart_config == expected_base_chart_config

    def test_chart_settings_width(self, fake_plot_data: PlotGenerationData):
        """
        Given a `width` integer
        When the `width` property is called from an instance of `ChartSettings`
        Then the correct number is returned
        """
        # Given
        width = 930
        payload = ChartGenerationPayload(
            chart_width=width,
            chart_height=220,
            plots=[fake_plot_data],
            x_axis_title="",
            y_axis_title="",
        )
        chart_settings = ChartSettings(chart_generation_payload=payload)

        # When
        chart_width: int = chart_settings.width

        # Then
        assert chart_width == width

    def test_chart_settings_height(self, fake_plot_data: PlotGenerationData):
        """
        Given a `width` integer
        When the `width` property is called from an instance of `ChartSettings`
        Then the correct number is returned
        """
        # Given
        height = 220
        payload = ChartGenerationPayload(
            chart_width=930,
            chart_height=height,
            plots=[fake_plot_data],
            x_axis_title="",
            y_axis_title="",
        )
        chart_settings = ChartSettings(chart_generation_payload=payload)

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
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given an instance of `ChartSettings`
        When `get_x_axis_date_type()` is called
        Then the correct config is returned
        """
        # Given
        payload = ChartGenerationPayload(
            chart_width=435,
            chart_height=220,
            plots=[fake_plot_data],
            x_axis_title="",
            y_axis_title="",
        )
        chart_settings = ChartSettings(chart_generation_payload=payload)

        # When
        x_axis_date_type = chart_settings.get_x_axis_date_type()

        # Then
        min_date, max_date = chart_settings.get_min_and_max_x_axis_values()
        max_date = get_max_date_for_current_month(existing_dt=max_date)

        expected_axis_config = {
            "type": "date",
            "dtick": "M1",
            "tickformat": "%b<br>%Y",
            "range": [min_date, max_date],
        }
        assert x_axis_date_type == expected_axis_config

    def test_get_x_axis_date_type_breaks_line_for_narrow_charts(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given an instance of `ChartSettings` with a narrow `width`
        When `get_x_axis_date_type()` is called
        Then the correct configuration for the x-axis is returned as a dict
        """
        # Given
        payload = ChartGenerationPayload(
            chart_width=435,
            chart_height=220,
            plots=[fake_plot_data],
            x_axis_title="",
            y_axis_title="",
        )
        chart_settings = ChartSettings(chart_generation_payload=payload)

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

    @mock.patch.object(ChartSettings, "build_line_single_simplified_axis_params")
    def test_get_line_single_simplified_chart_config(
        self,
        mock_build_line_single_simplified_axis_params: mock.MagicMock,
        fake_chart_settings: ChartSettings,
    ):
        """
        Given an instance of `ChartSettings`
        When `get_line_single_simplified_chart_config()` is called
        Then the correct configuration for
            `line_single_simplified` charts is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        fake_x_axis_tick_values = [0, 10]
        fake_x_axis_tick_text = ["tick01", "tick02"]
        fake_y_axis_tick_values = [0, 10]
        fake_y_axis_tick_text = ["tick01", "tick02"]

        mock_build_line_single_simplified_axis_params.return_value = {
            "x_axis_tick_values": fake_x_axis_tick_values,
            "x_axis_tick_text": fake_x_axis_tick_text,
            "y_axis_tick_values": fake_y_axis_tick_values,
            "y_axis_tick_text": fake_y_axis_tick_text,
        }

        # When
        line_single_simplified_chart_config = (
            chart_settings.get_line_single_simplified_chart_config()
        )

        # Then
        expected_chart_config = chart_settings.get_base_chart_config()
        # Chart settings
        expected_chart_config["showlegend"] = False
        expected_chart_config["margin"]["r"] = 35
        expected_chart_config["margin"]["l"] = 25
        expected_chart_config["margin"]["pad"] = 25

        # x_axis settings
        expected_chart_config["xaxis"]["showgrid"] = False
        expected_chart_config["xaxis"]["tickvals"] = fake_x_axis_tick_values
        expected_chart_config["xaxis"]["ticktext"] = fake_x_axis_tick_text
        expected_chart_config["xaxis"]["ticklen"] = 0
        expected_chart_config["xaxis"]["tickfont"][
            "color"
        ] = colour_scheme.RGBAColours.LS_DARK_GREY.stringified

        # y_axis settings
        expected_chart_config["yaxis"]["ticks"] = "outside"
        expected_chart_config["yaxis"]["zeroline"] = False
        expected_chart_config["yaxis"]["tickvals"] = fake_y_axis_tick_values
        expected_chart_config["yaxis"]["ticktext"] = fake_y_axis_tick_text
        expected_chart_config["yaxis"]["rangemode"] = "tozero"
        expected_chart_config["yaxis"]["ticklen"] = 0
        expected_chart_config["yaxis"]["tickfont"][
            "color"
        ] = colour_scheme.RGBAColours.LS_DARK_GREY.stringified

        assert line_single_simplified_chart_config == expected_chart_config

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

    def test_get_line_multi_coloured_chart_config(
        self, fake_chart_settings: ChartSettings
    ):
        """
        Given an instance of `ChartSettings`
        When `get_line_multi_coloured_chart_config()` is called
        Then the correct configuration for margins is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        line_multi_coloured_chart_config = (
            chart_settings.get_line_multi_coloured_chart_config()
        )

        # Then
        expected_line_multi_coloured_chart_config = {
            **chart_settings.get_base_chart_config(),
            **chart_settings._get_legend_top_centre_config(),
            "showlegend": True,
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
        fake_chart_settings._chart_generation_payload.chart_width = chart_width

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


class TestGetMaxDateForCurrentMonth:
    @pytest.mark.parametrize(
        "input_date",
        [
            "2024-02-01 12:00",
            "2024-02-02 12:00:98",
            "2024-02-03 19:07",
            "2024-02-04 23:20",
            "2024-02-05 12:09",
            "2024-02-06",
            "2024-02-07 11:59",
            "2024-02-08 14:30",
            "2024-02-09 16:00",
            "2024-02-10 00:00",
            "2024-02-11 16:00",
            "2024-02-12 00:00",
            "2024-02-13 14:30",
            "2024-02-14 16:00",
            "2024-02-15 11:00",
        ],
    )
    def test_returns_15th_if_current_day_less_than_10th(self, input_date: str):
        """
        Given an input date which is earlier
            than the 15th of that month
        When `get_max_date_for_current_month()` is called
        Then the 15th of that month is returned
        """
        # Given / When
        actual_date: datetime.date = get_max_date_for_current_month(
            existing_dt=input_date
        )

        # Then
        assert actual_date == datetime.date(year=2024, month=2, day=15)

    @pytest.mark.parametrize(
        "input_date, expected_date",
        [
            ("2024-02-16 12:00", datetime.date(year=2024, month=2, day=29)),
            ("2024-02-17 12:00:98", datetime.date(year=2024, month=2, day=29)),
            ("2024-02-18 19:07", datetime.date(year=2024, month=2, day=29)),
            ("2024-02-19 23:20", datetime.date(year=2024, month=2, day=29)),
            ("2024-02-22 12:09", datetime.date(year=2024, month=2, day=29)),
            ("2024-02-25", datetime.date(year=2024, month=2, day=29)),
            ("2024-02-26 16:00", datetime.date(year=2024, month=2, day=29)),
            ("2024-02-28 00:00", datetime.date(year=2024, month=2, day=29)),
        ],
    )
    def test_returns_current_date_if_greater_than_10th(
        self, input_date: str, expected_date: datetime.date
    ):
        """
        Given an input date which is older
            than the 10th of that month
        When `get_max_date_for_current_month()` is called
        Then the provided date is returned
        """
        # Given / When
        actual_date: datetime.date = get_max_date_for_current_month(
            existing_dt=input_date
        )

        # Then
        assert actual_date == expected_date
