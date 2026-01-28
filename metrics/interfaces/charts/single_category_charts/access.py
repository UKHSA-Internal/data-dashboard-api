import io
import urllib.parse
from datetime import datetime

import plotly.graph_objects
from django.db.models import Manager
from scour import scour

from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries
from metrics.domain.charts import (
    common_charts,
    line_single_simplified,
)
from metrics.domain.common.utils import (
    ChartTypes,
    extract_metric_group_from_metric,
)
from metrics.domain.models import (
    ChartGenerationPayload,
    ChartRequestParams,
    PlotGenerationData,
)
from metrics.domain.models.plots_text import PlotsText
from metrics.interfaces.charts.common.chart_output import ChartOutput
from metrics.interfaces.plots.access import PlotsInterface
from metrics.utils.type_hints import CORE_MODEL_MANAGER_TYPE

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects


class InvalidFileFormatError(Exception):
    def __init__(self):
        message = "Invalid file format, must be `svg`"
        super().__init__(message)


class InvalidChartTypeCombinationError(Exception):
    def __init__(self, invalid_chart_types: list[str]):
        message = f"There has been an invalid combination of plots selected, Please review your plot data. {', '.join(invalid_chart_types)}"
        super().__init__(message)


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

    @property
    def is_headline_data(self) -> bool:
        return self.chart_request_params.plots[0].is_headline_data

    @property
    def _is_common_chart_type(self) -> bool:
        """Checks to see if the requested chart_type(s) are for `common` or
            `uncommon` charts.

        Note:
            Common chart types include `bar` and `line_multi_coloured`, which can be combined
            into a single chart Eg: `bar_with_line`. Uncommon chart types are more specific
            in their use case and can not be combined with other types Eg: `line_single_simplified`.

            If multiple plots are requested and they include a combination of `common` and `uncommon`
            chart_types an `InvalidChartTypeCombinationError` will be raised that includes the `uncommon`
            chart_types provided
            in the request.

        Returns:
            Bool: Common = True, Uncommon = False
        """
        all_requested_chart_types: set[str] = {
            plot.chart_type for plot in self.chart_request_params.plots
        }

        if all_requested_chart_types.issubset(ChartTypes.common_chart_options()):
            return True

        if len(all_requested_chart_types) == 1:
            return False

        raise InvalidChartTypeCombinationError(
            all_requested_chart_types.intersection(ChartTypes.uncommon_chart_options())
        )

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
        if self.is_headline_data:
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

        figure = self._build_chart_figure(
            chart_generation_payload=chart_generation_payload,
        )

        return ChartOutput(
            figure=figure,
            description=description,
            is_headline=self.is_headline_data,
        )

    def _build_chart_figure(
        self, chart_generation_payload: ChartGenerationPayload
    ) -> plotly.graph_objects.Figure:
        """Builds a Plotly chart `Figure` object based on the chart type

        Args:
            chart_generation_payload: An enriched `ChartGenerationPayload` model
                which holds all the parameters like colour and plot labels
                 along with the corresponding x and y values
                 which are needed to be able to generate the chart in full.


        Returns:
            A plotly `Figure` object for the created chart type.
        """
        if self._is_common_chart_type:
            return self.generate_common_chart(
                chart_generation_payload=chart_generation_payload,
            )

        return self.generate_line_single_simplified(
            chart_generation_payload=chart_generation_payload
        )

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
    def generate_common_chart(
        cls,
        *,
        chart_generation_payload: ChartGenerationPayload,
    ) -> plotly.graph_objects.Figure:
        """Creates a `common` chart or a combination of multiple `common` charts

        Note:
            Common chart types include `bar` and `line_multi_coloured`, which can be combined
            into a single chart Eg: `bar_with_line`. Uncommon chart types are more specific

        Returns:
            A plotly `Figure` object for the created `common` chart

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries
        """
        return common_charts.generate_chart_figure(
            chart_generation_payload=chart_generation_payload
        )

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
            y_axis_minimum_value=self.chart_request_params.y_axis_minimum_value,
            y_axis_maximum_value=self.chart_request_params.y_axis_maximum_value,
            legend_title=self.chart_request_params.legend_title,
            confidence_intervals=self.chart_request_params.confidence_intervals,
            confidence_colour=self.chart_request_params.confidence_colour,
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

    def write_figure(self, *, figure: plotly.graph_objects.Figure) -> bytes:
        """
        Convert a figure to a static image and write to a file in the desired image format

        Args:
            figure: The figure object or a dictionary representing a figure

        Returns:
            The image in memory

        """
        file = io.BytesIO()

        figure.write_image(
            file=file,
            format=self.chart_request_params.file_format,
            validate=False,
        )

        file.seek(0)
        return file.getvalue()

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


def generate_chart_as_file(*, chart_request_params: ChartRequestParams) -> bytes:
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
