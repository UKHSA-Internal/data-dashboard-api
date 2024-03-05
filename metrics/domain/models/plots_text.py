from metrics.domain.models import PlotData, PlotParameters
from metrics.domain.utils import ChartTypes


class PlotsText:
    """This class is used to build alt_text for a chart/ list of enriched `PlotData` models"""

    def __init__(self, plots_data: list[PlotData]):
        self.plots_data: list[PlotData] = self._extract_plots_with_valid_data(
            plots_data=plots_data
        )

    @classmethod
    def _extract_plots_with_valid_data(
        cls, plots_data: list[PlotData]
    ) -> list[PlotData]:
        return [
            plot_data
            for plot_data in plots_data
            if plot_data.x_axis_values and plot_data.y_axis_values
        ]

    def construct_text(self) -> str:
        """Builds text describing all valid plots within the chart

        Returns:
            Single string describing the entire chart

        """
        plots_count: int = len(self.plots_data)
        text = ""

        match plots_count:
            case 0:
                text += self._introduce_no_plots()
            case 1:
                text += self._introduce_single_plot()
                text += self._describe_axes()
                text += self._describe_only_plot()
            case _:
                text += self._introduce_multiple_plots()
                text += self._describe_axes()
                text += self._describe_all_plots()

        return text

    @classmethod
    def _introduce_no_plots(cls) -> str:
        return "There is no data being shown for this chart."

    @classmethod
    def _introduce_single_plot(cls) -> str:
        return "There is only 1 plot on this chart. "

    def _introduce_multiple_plots(self) -> str:
        return f"There are {len(self.plots_data)} plots on this chart. "

    def _describe_axes(self) -> str:
        plot_parameters = self.plots_data[0].parameters
        return (
            f"The horizontal X-axis is labelled '{plot_parameters.x_axis}'. "
            f"Whilst the vertical Y-axis is labelled '{plot_parameters.y_axis}'. "
        )

    @classmethod
    def _stringify_chart_type(cls, plot_parameters: PlotData) -> str:
        chart_type: str = plot_parameters.chart_type
        match chart_type:
            case ChartTypes.bar.value:
                return "bar"
            case ChartTypes.line_multi_coloured.value:
                return "line"
            case ChartTypes.line_with_shaded_section.value:
                return "line"

    def _describe_only_plot(self) -> str:
        plot_parameters: PlotParameters = self.plots_data[0].parameters
        plot_type: str = self._stringify_chart_type(plot_parameters=plot_parameters)
        description = ""

        if plot_parameters.line_type and plot_parameters.line_colour:
            description += (
                f"The only plot on this chart "
                f"is a {plot_parameters.line_colour.lower()} {plot_parameters.line_type.lower()} {plot_type} plot. "
            )

        if plot_parameters.label:
            description += f"The plot has a label of '{plot_parameters.label}'. "

        description += self._describe_plot_parameters(plot_parameters=plot_parameters)

        return description

    @classmethod
    def _stringify_sex(cls, plot: PlotParameters) -> str:
        match plot.sex:
            case "f":
                return "females"
            case "m":
                return "males"
            case _:
                return "all"

    def _describe_plot_parameters(self, plot_parameters: PlotParameters) -> str:
        sex_grouping: str = self._stringify_sex(plot=plot_parameters)
        return (
            f"This plot shows data for {plot_parameters.topic}. "
            f"Specifically the metric '{plot_parameters.metric}' for the {plot_parameters.geography} area, "
            f"along with the age banding of '{plot_parameters.age}' for the gender group of {sex_grouping}. "
        )

    def _describe_all_plots(self) -> str:
        description = ""
        for index, plot_data in enumerate(self.plots_data, 1):
            plot_parameters = plot_data.parameters
            description += self._describe_next_plot_in_multiple_plot_group(
                index=index, plot_parameters=plot_parameters
            )
        return description

    def _describe_next_plot_in_multiple_plot_group(
        self, index: int, plot_parameters: PlotParameters
    ) -> str:
        plot_type: str = self._stringify_chart_type(plot_parameters=plot_parameters)

        description = (
            f"Plot number {index} on this chart "
            f"is a {plot_parameters.line_colour.lower()} {plot_parameters.line_type.lower()} {plot_type} plot. "
        )

        if plot_parameters.label:
            description += f"The plot has a label of '{plot_parameters.label}'. "

        description += self._describe_plot_parameters(plot_parameters=plot_parameters)

        return description
