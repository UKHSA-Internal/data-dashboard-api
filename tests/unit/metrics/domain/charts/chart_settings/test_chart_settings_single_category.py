import datetime
from unittest import mock

from _pytest.logging import LogCaptureFixture
import pytest

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings.base import ChartSettings
from metrics.domain.charts.chart_settings.single_category import (
    COMPACT_X_AXIS_NTICKS,
    FULL_WIDTH_X_AXIS_NTICKS,
    SingleCategoryChartSettings,
)
from metrics.domain.models import PlotGenerationData, ChartGenerationPayload
from tests.conftest import fake_plot_data

MODULE_PATH: str = "metrics.domain.charts.charts.chart_settings.single_category"


@pytest.fixture()
def fake_chart_settings(
    fake_plot_data: PlotGenerationData,
) -> SingleCategoryChartSettings:
    payload = ChartGenerationPayload(
        chart_width=930,
        chart_height=220,
        plots=[fake_plot_data],
        x_axis_title="Date",
        y_axis_title="Cases",
    )
    return SingleCategoryChartSettings(chart_generation_payload=payload)


class TestSingleCategoryChartSettings:
    def test_get_tick_font_setting(
        self, fake_chart_settings: SingleCategoryChartSettings
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
        When `get_tick_font_config()` is called
        Then the correct tick font configuration is returned as a dict.
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        tick_font_config = chart_settings._get_tick_font_config()

        # Then
        expected_tick_font_config = {
            "family": "Arial",
            "color": colour_scheme.RGBAColours.DARK_BLUE_GREY.stringified,
        }
        assert tick_font_config == expected_tick_font_config

    def test_get_x_axes_setting_for_date_based_x_axis(
        self, fake_chart_settings: SingleCategoryChartSettings
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
            with date-based x axes values
        When `get_x_axis_config()` is called
        Then the correct X axis configuration is return as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        x_axis_config = chart_settings._get_x_axis_config()

        # Then
        expected_x_axis_config = {
            "showspikes": True,
            "spikecolor": "#b1b4b6",
            "spikedash": "2px",
            "spikethickness": 1,
            "spikemode": "toaxis+across+marker",
            "spikesnap": "cursor",
            "showline": True,
            "fixedrange": True,
            "gridcolor": "rgba(0,0,0,0.05)",
            "linecolor": "rgba(0,0,0,0.05)",
            "tickcolor": "rgba(0,0,0,0)",
            "showgrid": True,
            "mirror": True,
            "zeroline": False,
            "ticks": "outside",
            "tickson": "boundaries",
            "type": "date",
            "tickfont": chart_settings._get_tick_font_config(),
            "autotickangles": [0, 90],
            "nticks": COMPACT_X_AXIS_NTICKS,
            "title": {
                "font": chart_settings._get_tick_font_config(),
                "text": chart_settings._chart_generation_payload.x_axis_title,
            },
        }
        expected_x_axis_config = {
            **expected_x_axis_config,
            **chart_settings.get_x_axis_date_type(),
        }
        assert x_axis_config == expected_x_axis_config

    def test_get_x_axes_setting_for_text_based_x_axis(
        self, fake_chart_settings: SingleCategoryChartSettings
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
            with text-based x axes values
        When `get_x_axis_config()` is called
        Then the correct X axis configuration is return as a dict
        """
        # Given
        chart_settings = fake_chart_settings
        original_values = chart_settings.plots_data[0].x_axis_values
        chart_settings.plots_data[0].x_axis_values = [
            f"P-{i}" for i in range(len(original_values))
        ]

        # When
        x_axis_config = chart_settings._get_x_axis_config()

        # Then
        expected_x_axis_config = {
            "showspikes": True,
            "spikecolor": "#b1b4b6",
            "spikedash": "2px",
            "spikethickness": 1,
            "spikemode": "toaxis+across+marker",
            "spikesnap": "cursor",
            "showline": True,
            "showgrid": True,
            "zeroline": False,
            "fixedrange": True,
            "mirror": True,
            "gridcolor": "rgba(0,0,0,0.05)",
            "linecolor": "rgba(0,0,0,0.05)",
            "tickcolor": "rgba(0,0,0,0)",
            "ticks": "outside",
            "tickson": "boundaries",
            "type": "-",
            "dtick": None,
            "tickformat": None,
            "tickfont": chart_settings._get_tick_font_config(),
            "autotickangles": [0, 90],
            "nticks": COMPACT_X_AXIS_NTICKS,
            "title": {
                "font": chart_settings._get_tick_font_config(),
                "text": chart_settings._chart_generation_payload.x_axis_title,
            },
        }
        assert x_axis_config == expected_x_axis_config

    def test_get_y_axes_setting(self, fake_chart_settings: SingleCategoryChartSettings):
        """
        Given an instance of `SingleCategoryChartSettings`
        When `get_y_axis_config()` is called
        Then the correct Y axis configuration is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        y_axis_config = chart_settings._get_y_axis_config()

        # Then
        expected_y_axis_config = {
            "rangemode": "tozero",
            "showgrid": True,
            "showline": True,
            "linecolor": "rgba(0,0,0,0.05)",
            "mirror": True,
            "showticklabels": True,
            "fixedrange": True,
            "gridcolor": "rgba(0,0,0,0.05)",
            "ticks": "outside",
            "tickson": "boundaries",
            "tickformatstops": [
                {"dtickrange": [None, 999], "value": ","},
                {"dtickrange": [1000, 99999], "value": ",.0f"},
                {"dtickrange": [100000, None], "value": ".0s"},
            ],
            "tickcolor": "rgba(0,0,0,0)",
            "tickfont": chart_settings._get_tick_font_config(),
            "tick0": 0,
            "title": {
                "font": chart_settings._get_tick_font_config(),
                "text": chart_settings._chart_generation_payload.y_axis_title,
            },
        }
        assert y_axis_config == expected_y_axis_config

    @mock.patch.object(SingleCategoryChartSettings, "_get_y_axis_config")
    @mock.patch.object(SingleCategoryChartSettings, "_get_x_axis_config")
    def test_get_base_chart_config(
        self,
        mocked_get_x_axis_config: mock.MagicMock,
        mocked_get_y_axis_config: mock.MagicMock,
        fake_chart_settings: SingleCategoryChartSettings,
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
        When `get_base_chart_config()` is called
        Then the correct base chart configuration is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        base_chart_config = chart_settings._get_base_chart_config()

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
        When the `width` property is called from an instance of `SingleCategoryChartSettings`
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
        chart_settings = SingleCategoryChartSettings(chart_generation_payload=payload)

        # When
        chart_width: int = chart_settings.width

        # Then
        assert chart_width == width

    def test_chart_settings_height(self, fake_plot_data: PlotGenerationData):
        """
        Given a `height` integer
        When the `height` property is called from an instance of `SingleCategoryChartSettings`
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
        chart_settings = SingleCategoryChartSettings(chart_generation_payload=payload)

        # When
        chart_height: int = chart_settings.height

        # Then
        assert chart_height == height

    def test_get_x_axis_date_type(
        self, fake_chart_settings: SingleCategoryChartSettings
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
        When `get_x_axis_date_type()` is called
        Then the correct configuration for the x-axis is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings

        # When
        x_axis_date_type = chart_settings.get_x_axis_date_type()

        # Then
        assert x_axis_date_type["type"] == "date"
        assert x_axis_date_type["autorange"] is True
        assert "range" not in x_axis_date_type
        assert "dtick" not in x_axis_date_type
        assert "nticks" not in x_axis_date_type
        assert x_axis_date_type["tickformatstops"] == [
            {"dtickrange": ["M12", None], "value": "%Y"},
            {"dtickrange": ["M1", "M12"], "value": "%b %Y"},
            {"dtickrange": [None, "M1"], "value": "%d %b<br>%Y"},
        ]

    def test_get_x_axis_date_type_breaks_month_and_year_for_narrow_charts(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given an instance of `SingleCategoryChartSettings` with a narrow `width`
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
        chart_settings = SingleCategoryChartSettings(chart_generation_payload=payload)

        # When
        x_axis_date_type = chart_settings.get_x_axis_date_type()

        # Then
        assert x_axis_date_type["tickformatstops"][1]["value"] == "%b<br>%Y"

    @pytest.mark.parametrize(
        ("chart_width", "expected_nticks"),
        (
            (1099, COMPACT_X_AXIS_NTICKS),
            (1100, FULL_WIDTH_X_AXIS_NTICKS),
            (1200, FULL_WIDTH_X_AXIS_NTICKS),
        ),
    )
    def test_get_x_axis_nticks_uses_chart_width(
        self,
        chart_width: int,
        expected_nticks: int,
        fake_chart_settings: SingleCategoryChartSettings,
    ):
        fake_chart_settings._chart_generation_payload.chart_width = chart_width

        assert fake_chart_settings.get_x_axis_nticks() == expected_nticks

    def test_get_x_axis_config_applies_nticks_to_text_axes(
        self, fake_chart_settings: SingleCategoryChartSettings
    ):
        fake_chart_settings.plots_data[0].x_axis_values = [
            "category-1",
            "category-2",
        ]

        x_axis_config = fake_chart_settings._get_x_axis_config()

        assert x_axis_config["nticks"] == COMPACT_X_AXIS_NTICKS

    def test_get_x_axis_text_type(
        self, fake_chart_settings: SingleCategoryChartSettings
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
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

    def test_build_line_single_simplified_y_axis_vaue_params_with_zero_min_value(
        self,
        fake_plot_data: PlotGenerationData,
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
        When `build_line_single_simplified_y_axis_value_params` is called with
            a valid payload where the `y_axis_minimum_value` is omitted
        Then a dictionary is returned with the expected values including `tick_values`
            and `range` where the first item in the list is 0
        """
        # Given
        fake_plot_data.y_axis_values = [2000, 2550, 2300, 4000, 3500, 6000, 5480]
        payload = ChartGenerationPayload(
            chart_width=435,
            chart_height=220,
            plots=[fake_plot_data],
            y_axis_maximum_value=7000,
            y_axis_title="",
            x_axis_title="",
        )
        chart_settings = SingleCategoryChartSettings(chart_generation_payload=payload)

        # When
        returned_y_axis_params = (
            chart_settings._build_line_single_simplified_y_axis_value_params()
        )
        expected_y_axis_params = {
            "y_axis_tick_values": [0, 7000],
            "y_axis_tick_text": ["0", "7k"],
            "range": [0, 7000],
        }

        # Then
        assert expected_y_axis_params == returned_y_axis_params

    def test_build_line_single_simplified_y_axis_value_params_with_valid_min_and_max_value(
        self,
        fake_plot_data: PlotGenerationData,
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
        When `build_line_single_simplified_y_axis_value_params` is called with
            a valid payload including a `min` and `max` value to override the `y_axis_values`
        Then a dictionary is returned with the expected values including `tick_values`
            and `range` that include the provided min and max values.
        """
        # Given
        fake_plot_data.y_axis_values = [2000, 2550, 2300, 4000, 3500, 6000, 5480]
        payload = ChartGenerationPayload(
            chart_width=435,
            chart_height=220,
            plots=[fake_plot_data],
            y_axis_minimum_value=1000,
            y_axis_maximum_value=7000,
            y_axis_title="",
            x_axis_title="",
        )
        chart_settings = SingleCategoryChartSettings(chart_generation_payload=payload)

        # When
        returned_y_axis_params = (
            chart_settings._build_line_single_simplified_y_axis_value_params()
        )
        expected_y_axis_params = {
            "y_axis_tick_values": [1000, 7000],
            "y_axis_tick_text": ["1k", "7k"],
            "range": [1000, 7000],
        }

        # Then
        assert expected_y_axis_params == returned_y_axis_params

    def test_build_line_single_simplified_y_axis_value_params_with_invalid_min_value(
        self,
        fake_plot_data: PlotGenerationData,
        caplog: LogCaptureFixture,
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
        When `build_line_single_simplified_y_axis_value_params` is called with
            an invalid `y_axis_minimum_value` meaning that the value provided is larger
            than the minimum value found in the data
        Then the provided value is bypassed and the lowest value from the data is used
            instead, this override is then logged for transparency
        """
        # Given
        fake_plot_data.y_axis_values = [2000, 2550, 2300, 4000, 3500, 6000, 5480]
        payload = ChartGenerationPayload(
            chart_width=435,
            chart_height=220,
            plots=[fake_plot_data],
            y_axis_minimum_value=3000,
            y_axis_maximum_value=7000,
            y_axis_title="",
            x_axis_title="",
        )
        chart_settings = SingleCategoryChartSettings(chart_generation_payload=payload)

        # When
        returned_y_axis_params = (
            chart_settings._build_line_single_simplified_y_axis_value_params()
        )
        expected_y_axis_params = {
            "y_axis_tick_values": [2000, 7000],
            "y_axis_tick_text": ["2k", "7k"],
            "range": [2000, 7000],
        }

        # Then
        assert expected_y_axis_params == returned_y_axis_params

    def test_build_line_single_simplified_y_axis_value_params_with_invalid_max_value(
        self,
        fake_plot_data: PlotGenerationData,
        caplog: LogCaptureFixture,
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
        When `build_line_single_simplified_y_axis_value_params` is called with
            an invalid `y_axis_maximum_value` meaning that the value provided is lower
            than the maximum value found in the data
        Then the provided value is bypassed and the highest value from the data is used
            instead, this override is then logged for transparency
        """
        # Given
        fake_plot_data.y_axis_values = [2000, 2550, 2300, 4000, 3500, 6000, 5480]
        payload = ChartGenerationPayload(
            chart_width=435,
            chart_height=220,
            plots=[fake_plot_data],
            y_axis_minimum_value=1000,
            y_axis_maximum_value=5000,
            y_axis_title="",
            x_axis_title="",
        )
        chart_settings = SingleCategoryChartSettings(chart_generation_payload=payload)

        # When
        returned_y_axis_params = (
            chart_settings._build_line_single_simplified_y_axis_value_params()
        )
        expected_y_axis_params = {
            "y_axis_tick_values": [1000, 6000],
            "y_axis_tick_text": ["1k", "6k"],
            "range": [1000, 6000],
        }

        # Then
        assert expected_y_axis_params == returned_y_axis_params

    @mock.patch.object(
        SingleCategoryChartSettings, "_build_line_single_simplified_axis_params"
    )
    def test_get_line_single_simplified_chart_config(
        self,
        mock_build_line_single_simplified_axis_params: mock.MagicMock,
        fake_chart_settings: SingleCategoryChartSettings,
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
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
        # min and max value for manual y-axis input
        fake_y_axis_range = [0, 10]
        fake_y_axis_rangemode = "tozero"

        mock_build_line_single_simplified_axis_params.return_value = {
            "x_axis_tick_values": fake_x_axis_tick_values,
            "x_axis_tick_text": fake_x_axis_tick_text,
            "y_axis_tick_values": fake_y_axis_tick_values,
            "y_axis_tick_text": fake_y_axis_tick_text,
            "range": fake_y_axis_range,
            "rangemode": fake_y_axis_rangemode,
        }

        # When
        line_single_simplified_chart_config = (
            chart_settings.get_line_single_simplified_chart_config()
        )

        # Then
        expected_chart_config = chart_settings._get_base_chart_config()
        # Chart settings
        expected_chart_config["showlegend"] = False
        expected_chart_config["margin"]["r"] = 35
        expected_chart_config["margin"]["l"] = 25
        expected_chart_config["margin"]["t"] = 12
        expected_chart_config["margin"]["pad"] = 25

        # x_axis settings
        expected_chart_config["xaxis"]["showgrid"] = False
        expected_chart_config["xaxis"]["showline"] = False
        expected_chart_config["xaxis"]["mirror"] = False
        expected_chart_config["xaxis"]["tickvals"] = fake_x_axis_tick_values
        expected_chart_config["xaxis"]["ticktext"] = fake_x_axis_tick_text
        expected_chart_config["xaxis"]["ticklen"] = 0
        expected_chart_config["xaxis"]["tickfont"][
            "color"
        ] = colour_scheme.RGBAColours.LS_DARK_GREY.stringified

        # y_axis settings
        expected_chart_config["yaxis"]["showgrid"] = False
        expected_chart_config["yaxis"]["showline"] = False
        expected_chart_config["yaxis"]["mirror"] = False
        expected_chart_config["yaxis"]["ticks"] = "outside"
        expected_chart_config["yaxis"]["zeroline"] = False
        expected_chart_config["yaxis"]["tickvals"] = fake_y_axis_tick_values
        expected_chart_config["yaxis"]["ticktext"] = fake_y_axis_tick_text
        expected_chart_config["yaxis"]["ticklen"] = 0
        expected_chart_config["yaxis"]["tickfont"][
            "color"
        ] = colour_scheme.RGBAColours.LS_DARK_GREY.stringified
        expected_chart_config["yaxis"]["range"] = fake_y_axis_range
        expected_chart_config["yaxis"]["rangemode"] = fake_y_axis_rangemode

        assert line_single_simplified_chart_config == expected_chart_config

    def test_get_legend_top_centre_config(
        self, fake_chart_settings: SingleCategoryChartSettings
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
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
                "font": {
                    "color": colour_scheme.RGBAColours.DARK_BLUE_GREY.stringified,
                    "family": "Arial",
                },
                "orientation": "h",
                "y": 1.0,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "bottom",
            },
        }
        assert legend_top_centre_config == expected_legend_top_centre_config

    def test_get_legend_top_centre_config_includes_legend_title_when_provided(
        self, fake_chart_settings: ChartSettings
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
            which includes a legend title
        When `_get_legend_top_centre_config()` is called
        Then the correct configuration for the legend is returned as a dict
        """
        # Given
        chart_settings = fake_chart_settings
        legend_title = "Level of coverage (%)"
        chart_settings._chart_generation_payload.legend_title = legend_title

        # When
        legend_top_centre_config = chart_settings._get_legend_top_centre_config()

        # Then
        expected_legend_top_centre_config = {
            "legend": {
                "title": f"<b>{legend_title}</b>",
                "font": {
                    "color": colour_scheme.RGBAColours.DARK_BLUE_GREY.stringified,
                    "family": "Arial",
                },
                "orientation": "h",
                "y": 1.0,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "bottom",
            },
        }
        assert legend_top_centre_config == expected_legend_top_centre_config

    def test_get_line_multi_coloured_chart_config(
        self,
        fake_chart_settings: SingleCategoryChartSettings,
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
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
            **chart_settings._get_base_chart_config(),
            **chart_settings._get_legend_top_centre_config(),
            "showlegend": True,
        }

        assert (
            line_multi_coloured_chart_config
            == expected_line_multi_coloured_chart_config
        )

    @pytest.mark.parametrize(
        "y_axis_min, y_axis_max, expected_y_axis_min, expected_y_axis_max, y_axis_values",
        (
            [200, 10000, 100, 10000, [100, 200, 300, 400, 500]],
            [100, 10000, 100, 10000, [500, 1000, 1500, 2000]],
            [100, 1000, 100, 2000, [500, 1000, 1500, 2000]],
        ),
    )
    def test_get_line_multi_coloured_chart_config_returns_correct_y_axis_range(
        self,
        fake_chart_settings: SingleCategoryChartSettings,
        y_axis_min: int,
        y_axis_max: int | None,
        expected_y_axis_min: int,
        expected_y_axis_max: int,
        y_axis_values: list[int],
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
        When the `get_line_multi_coloured_chart_config()` method is called
            provided manual y-axis min and max values
        Then the correct chart settings are returned
        """
        # Given
        fake_chart_settings._chart_generation_payload.y_axis_minimum_value = y_axis_min
        fake_chart_settings._chart_generation_payload.y_axis_maximum_value = y_axis_max
        fake_chart_settings.plots_data[0].y_axis_values = y_axis_values

        # When
        line_multi_coloured_chart_config = (
            fake_chart_settings.get_line_multi_coloured_chart_config()
        )

        # Then
        assert line_multi_coloured_chart_config["yaxis"]["range"] == [
            expected_y_axis_min,
            expected_y_axis_max,
        ]
        assert line_multi_coloured_chart_config["yaxis"]["tick0"] == expected_y_axis_min

    @pytest.mark.parametrize(
        "chart_width, expected_date_tick_format", ([430, "%b<br>%Y"], [930, "%b %Y"])
    )
    def test_get_date_tick_format(
        self,
        chart_width: int,
        expected_date_tick_format: str,
        fake_chart_settings: SingleCategoryChartSettings,
    ):
        """
        Given an instance of `SingleCategoryChartSettings`
        When `_get_date_tick_format()` is called
        Then the correct string is returned
        """
        # Given
        fake_chart_settings._chart_generation_payload.chart_width = chart_width

        # When
        returned_date_tick_format: str = fake_chart_settings._get_date_tick_format()

        # Then
        assert returned_date_tick_format == expected_date_tick_format
