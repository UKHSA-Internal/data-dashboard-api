import urllib.parse
from dataclasses import dataclass
from datetime import datetime

import plotly.graph_objects
from django.db.models import Manager
from scour import scour

from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries
from metrics.domain.charts import (
    bar,
    line_multi_coloured,
    line_single_simplified,
    line_with_shaded_section,
)
from metrics.domain.common.utils import (
    ChartTypes,
    DataSourceFileType,
    extract_metric_group_from_metric,
)
from metrics.domain.models import (
    ChartGenerationPayload,
    ChartRequestParams,
    PlotGenerationData,
)
from metrics.domain.models.plots_text import PlotsText
from metrics.interfaces.charts import calculations
from metrics.interfaces.plots.access import PlotsInterface
from metrics.utils.type_hints import CORE_MODEL_MANAGER_TYPE

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects
HEX_COLOUR_BLACK = "#0b0c0c"


class InvalidFileFormatError(Exception):
    def __init__(self):
        message = "Invalid file format, must be `svg`"
        super().__init__(message)


@dataclass
class ChartOutput:
    figure: plotly.graph_objects.Figure
    description: str

    @property
    def interactive_chart_figure_output(self) -> dict:
        self._add_settings_for_interactive_charts()
        return self.figure.to_dict()

    @property
    def _interactive_charts_font_css_var(self):
        return "var(--font-primary), arial, sans-serif"

    def _add_settings_for_interactive_charts(self):
        self._unset_width()
        self._apply_font_to_ticks()
        self._apply_x_axis_styling()

        self._apply_autosizing()

        self._apply_hover_label_styling()
        self._disable_clicks_on_legend()
        self._apply_hover_template_to_all_plots()

    def _unset_width(self):
        self.figure.layout.width = None

    def _apply_font_to_ticks(self):
        self.figure.layout.xaxis.tickfont.update(
            family=self._interactive_charts_font_css_var
        )
        self.figure.layout.yaxis.tickfont.update(
            family=self._interactive_charts_font_css_var
        )

    def _apply_x_axis_styling(self):
        self.figure.layout.xaxis.showline = True
        self.figure.layout.xaxis.showspikes = False

    def _apply_autosizing(self):
        self.figure.layout.autosize = True

    def _apply_hover_label_styling(self):
        self.figure.layout.hoverlabel.bgcolor = HEX_COLOUR_BLACK
        self.figure.layout.hoverlabel.bordercolor = HEX_COLOUR_BLACK
        self.figure.layout.hoverlabel.font.update(
            size=16,
            color="white",
            family=self._interactive_charts_font_css_var,
        )

    def _apply_hover_template_to_all_plots(self):
        for plot in self.figure.data:
            plot.hovertemplate = "%{y} <extra></extra>"

    def _disable_clicks_on_legend(self):
        self.figure.layout.legend.itemclick = False
        self.figure.layout.legend.itemdoubleclick = False


class ChartsInterface:
    def __init__(
        self,
        *,
        chart_request_params: ChartRequestParams,
        core_model_manager: CORE_MODEL_MANAGER_TYPE | None = None,
        plots_interface: PlotsInterface | None = None,
    ):
        self.chart_request_params = chart_request_params
        self.chart_type = self.chart_request_params.plots[0].chart_type
        self.metric_group = extract_metric_group_from_metric(
            metric=self.chart_request_params.plots[0].metric
        )
        self.core_model_manager = core_model_manager or self._set_core_model_manager()

        self.plots_interface = plots_interface or PlotsInterface(
            chart_request_params=self.chart_request_params,
            core_model_manager=self.core_model_manager,
        )

        self._latest_date: str = ""

    def _set_core_model_manager(self) -> Manager:
        """Returns `core_model_manager` based on the `metric_group`

        Notes:
            The charts interface can be used to generate charts for
            either `CoreTimeSeries` or `CoreHeadline` data.
            this function returns the Django manager to match the
            current `metric_group` or defaults to `CoreTimeseries`
            manager

        Returns:
            Manager: either `CoreTimeseries` or `CoreHeadline`
        """
        if DataSourceFileType[self.metric_group].is_headline:
            return DEFAULT_CORE_HEADLINE_MANAGER

        return DEFAULT_CORE_TIME_SERIES_MANAGER

    def generate_chart_output(self) -> ChartOutput:
        """Generates a `plotly` chart figure and a corresponding description

        Returns:
            An enriched `ChartOutput` model containing:
                figure - a plotly `Figure` object for the created chart
                description - a string representation
                    which summarises the produced chart

        """
        chart_generation_payload: ChartGenerationPayload = (
            self.build_chart_generation_payload()
        )
        description = self.build_chart_description(
            plots_data=chart_generation_payload.plots
        )

        match self.chart_type:
            case ChartTypes.bar.value:
                figure = self.generate_bar_chart(
                    chart_generation_payload=chart_generation_payload
                )
            case ChartTypes.line_multi_coloured.value:
                figure = self.generate_line_multi_coloured_chart(
                    chart_generation_payload=chart_generation_payload
                )
            case ChartTypes.line_single_simplified.value:
                figure = self.generate_line_single_simplified(
                    chart_generation_payload=chart_generation_payload
                )
            case _:
                figure = self.generate_line_with_shaded_section_chart(
                    chart_generation_payload=chart_generation_payload
                )

        return ChartOutput(figure=figure, description=description)

    @classmethod
    def build_chart_description(cls, *, plots_data: list[PlotGenerationData]) -> str:
        """Creates a description to summarize the contents of the chart.

        Args:
            plots_data: List of `PlotData` models,
                where each model represents a requested plot.
                Note that each `PlotData` model is enriched with data
                with the according x and y values along with
                requests parameters like colour and plot label.

        Returns:
            Single string describing the entire chart

        """
        plots_text = PlotsText(plots_data=plots_data)
        return plots_text.construct_text()

    @classmethod
    def generate_bar_chart(
        cls,
        *,
        chart_generation_payload: ChartGenerationPayload,
    ) -> plotly.graph_objects.Figure:
        """Creates a bar chart figure for the requested chart plot

        Notes
            This does support **multiple** plots on the same figure

        Args:
            chart_generation_payload: An enriched `ChartGenerationPayload` model
                which holds all the parameters like colour and plot labels
                 along with the corresponding x and y values
                 which are needed to be able to generate the chart in full.

        Returns:
            A plotly `Figure` object for the created bar chart

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries

        """
        return bar.generate_chart_figure(
            chart_generation_payload=chart_generation_payload
        )

    @classmethod
    def generate_line_multi_coloured_chart(
        cls,
        *,
        chart_generation_payload: ChartGenerationPayload,
    ) -> plotly.graph_objects.Figure:
        """Creates a multiple line colour-differentiated chart figure for the requested chart plots

        Notes
            This does support **multiple** plots on the same figure

        Args:
            chart_generation_payload: An enriched `ChartGenerationPayload` model
                which holds all the parameters like colour and plot labels
                 along with the corresponding x and y values
                 which are needed to be able to generate the chart in full.

        Returns:
            A plotly `Figure` object for the created multi-coloured line chart

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries
        """
        return line_multi_coloured.generate_chart_figure(
            chart_generation_payload=chart_generation_payload
        )

    def generate_line_with_shaded_section_chart(
        self,
        *,
        chart_generation_payload: ChartGenerationPayload,
    ) -> plotly.graph_objects.Figure:
        """Creates a line chart with shaded section figure for the requested chart plot

        Notes:
            Currently on the first requested chart plot is used,
            the remaining plots are not applied to the figure.

        Args:
            chart_generation_payload: An enriched `ChartGenerationPayload` model
                which holds all the parameters like colour and plot labels
                 along with the corresponding x and y values
                 which are needed to be able to generate the chart in full.

        Returns:
            A plotly `Figure` object for the created line chart with shaded section

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries

        """
        params = self.param_builder_for_line_with_shaded_section(
            plots_data=chart_generation_payload.plots
        )
        return line_with_shaded_section.generate_chart_figure(**params)

    @classmethod
    def generate_line_single_simplified(
        cls,
        *,
        chart_generation_payload: ChartGenerationPayload,
    ) -> plotly.graph_objects.Figure:
        """Creates a simplified line chart with only 4 tick labels displayed for the first
            and last values on each axis

        Notes:
            Only the first requested chart_plot is provided to the
            simplified chart.

        Args:
            chart_generation_payload: An enriched `ChartGenerationPayload` model
                which holds all the parameters like colour and plot labels
                 along with the corresponding x and y values
                 which are needed to be able to generate the chart in full.

        Returns:
            A plotly `Figure` object for the created line chart with shaded section

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries

        """
        return line_single_simplified.generate_chart_figure(
            chart_generation_payload=chart_generation_payload
        )

    def build_chart_generation_payload(self) -> ChartGenerationPayload:
        plots_data: list[PlotGenerationData] = self._build_chart_plots_data()
        return ChartGenerationPayload(
            plots=plots_data,
            x_axis_title=self.chart_request_params.x_axis_title,
            y_axis_title=self.chart_request_params.y_axis_title,
            chart_height=self.chart_request_params.chart_height,
            chart_width=self.chart_request_params.chart_width,
        )

    def _build_chart_plots_data(self) -> list[PlotGenerationData]:
        """Creates a list of `PlotData` models which hold the params and corresponding data for the requested plots

        Notes:
            The corresponding timeseries data is used to enrich a
            pydantic model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

            If no data is returned for a particular plot,
            that chart plot is skipped and
            an enriched model will not be provided.

        Returns:
            A list of `PlotData` models for each of the requested chart plots.

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries

        """
        plots_data: list[PlotGenerationData] = self.plots_interface.build_plots_data()
        self._set_latest_date_from_plots_data(plots_data=plots_data)

        return plots_data

    def _set_latest_date_from_plots_data(
        self, *, plots_data: list[PlotGenerationData]
    ) -> None:
        """Extracts the latest date from the list of given `plots_data`

        Notes:
            This extracted value is set on the `_latest_date`
            instance attribute on this object

        Args:
            plots_data: List of `PlotData` models,
                where each model represents a requested plot.
                Note that each `PlotData` model is enriched
                with the according x and y values along with
                requests parameters like colour and plot label.

        Returns:
            None

        """
        try:
            latest_date: datetime.date = max(plot.latest_date for plot in plots_data)
        except (ValueError, TypeError):
            return

        self._latest_date: str = datetime.strftime(latest_date, "%Y-%m-%d")

    def param_builder_for_line_with_shaded_section(
        self, *, plots_data: list[PlotGenerationData]
    ):
        plot_data = plots_data[0]
        chart_height = self.chart_request_params.chart_height
        chart_width = self.chart_request_params.chart_width
        x_axis_values = plot_data.x_axis_values
        y_axis_values = plot_data.y_axis_values
        metric_name = plot_data.parameters.metric_name

        return {
            "plots_data": plots_data,
            "chart_height": chart_height,
            "chart_width": chart_width,
            "x_axis_values": x_axis_values,
            "y_axis_values": y_axis_values,
            "metric_name": metric_name,
            "change_in_metric_value": self.calculate_change_in_metric_value(
                values=y_axis_values,
                metric_name=metric_name,
            ),
            "rolling_period_slice": calculations.get_rolling_period_slice_for_metric(
                metric_name=metric_name
            ),
        }

    def param_builder_for_line_single_simplified(
        self, *, plots_data: list[PlotGenerationData]
    ):
        """Returns the params required to create a
            `line_single_simplified` chart.

        Args:
            plots_data: list of `PlotData` models

        Returns:
            A dict of chart properties, this line chart
            only supports a single plot so only the first
            plots_data item is returned in the `plot_data`
            list if more than one is supplied.
        """
        plot_data = plots_data[0]
        chart_height = self.chart_request_params.chart_height
        chart_width = self.chart_request_params.chart_width

        return {
            "plot_data": [plot_data],
            "chart_height": chart_height,
            "chart_width": chart_width,
        }

    def create_optimized_svg(self, *, figure: plotly.graph_objects.Figure) -> str:
        """Convert figure to a `svg` then optimize the size of it

        Args:
            figure: The figure object or a dictionary representing a figure

        Returns:
            A figure as an image and optimized for size if required
        """
        svg_image = figure.to_image(
            format=self.chart_request_params.file_format, validate=False
        )
        return scour.scourString(in_string=svg_image)

    def encode_figure(self, *, figure: plotly.graph_objects.Figure) -> str:
        """
        URI Encode the supplied chart figure

        Args:
            figure: The figure object or a dictionary representing a figure

        Returns:
            An encoded string representation of the figure

        """
        if self.chart_request_params.file_format != "svg":
            raise InvalidFileFormatError

        optimized_svg: str = self.create_optimized_svg(figure=figure)

        encoded_chart: str = urllib.parse.quote_plus(optimized_svg)

        return encoded_chart

    def write_figure(self, *, figure: plotly.graph_objects.Figure) -> str:
        """
        Convert a figure to a static image and write to a file in the desired image format

        Args:
            figure: The figure object or a dictionary representing a figure

        Returns:
            The filename of the image

        """
        filename = f"new_chart.{self.chart_request_params.file_format}"
        figure.write_image(
            file=filename,
            format=self.chart_request_params.file_format,
            validate=False,
        )

        return filename

    @staticmethod
    def calculate_change_in_metric_value(*, values, metric_name) -> int | float:
        rolling_period_slice: int = calculations.get_rolling_period_slice_for_metric(
            metric_name=metric_name
        )
        preceding_slice: int = rolling_period_slice * 2

        values = values[-preceding_slice:]

        return calculations.change_between_each_half(values=values)

    def get_encoded_chart(self, *, chart_output: ChartOutput) -> dict[str, str | dict]:
        """Creates a dict containing a timestamp for the last data point + encoded string for the chart figure.

        Args:
            chart_output: An enriched `ChartOutput` model containing:
                figure - a plotly `Figure` object for the created chart
                description - a string representation
                    which summarises the produced chart

        Returns:
            A dict containing:
             "last_updated": A timestamp for the last data point
             "chart": An encoded string representing the chart figure
             "alt_text": A string representation of the chart description

        """
        return {
            "last_updated": self._latest_date,
            "chart": self.encode_figure(figure=chart_output.figure),
            "alt_text": chart_output.description,
            "figure": chart_output.interactive_chart_figure_output,
        }


def generate_chart_as_file(*, chart_request_params: ChartRequestParams) -> str:
    """Validates and creates a chart figure based on the parameters provided within the `chart_plots` model

    Args:
        chart_request_params: The requested chart request
            parameters encapsulated as a model

    Returns:
        The filename of the created image

    Raises:
        `InvalidPlotParametersError`: If an underlying
            validation check has failed.
            This could be because there is
            an invalid topic and metric selection.
            Or because the selected dates are not in
            the expected chronological order.
        `DataNotFoundForAnyPlotError`: If no plots
            returned any data from the underlying queries

    """
    charts_interface = ChartsInterface(chart_request_params=chart_request_params)
    chart_output: ChartOutput = charts_interface.generate_chart_output()

    return charts_interface.write_figure(figure=chart_output.figure)


def generate_encoded_chart(
    *, chart_request_params: ChartRequestParams
) -> dict[str, str]:
    """Validates and creates a chart figure based on the parameters provided within the `chart_plots` model
     Then encodes it, adds the last_updated_date to it and returns the result as a serialized JSON string

    Args:
        chart_request_params: The requested chart plot
            parameters encapsulated as a model

    Returns:
        A dict containing:
         "last_updated": A timestamp for the last data point
         "chart": An encoded string representing the chart figure

    Raises:
        `InvalidPlotParametersError`: If an underlying
            validation check has failed.
            This could be because there is
            an invalid topic and metric selection.
            Or because the selected dates are not in
            the expected chronological order.
        `DataNotFoundForAnyPlotError`: If no plots
            returned any data from the underlying queries

    """
    charts_interface = ChartsInterface(chart_request_params=chart_request_params)
    chart_output: ChartOutput = charts_interface.generate_chart_output()

    return charts_interface.get_encoded_chart(chart_output=chart_output)
