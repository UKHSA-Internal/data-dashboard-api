import contextlib
import datetime
from collections.abc import Iterator
from decimal import Decimal
from typing import Any

from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.charts.line_multi_coloured.properties import ChartLineTypes
from metrics.domain.charts.reporting_delay_period import (
    get_x_value_at_start_of_reporting_delay_period,
)
from metrics.domain.common.utils import ChartTypes
from metrics.domain.models import PlotData, PlotParameters
from metrics.domain.models.plots import (
    NoReportingDelayPeriodFoundError,
    ReportingDelayNotProvidedToPlotsError,
)

READABLE_DATE_FORMAT = "%d %B %Y"


class PlotsText:
    """This class is used to build alt_text for a chart/ list of enriched `PlotData` models"""

    def __init__(self, *, plots_data: list[PlotData]):
        self.plots_data: list[PlotData] = self._extract_plots_with_valid_data(
            plots_data=plots_data
        )

    @classmethod
    def _extract_plots_with_valid_data(
        cls, *, plots_data: list[PlotData]
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
                text += self._describe_reporting_delay_period()
            case _:
                text += self._introduce_multiple_plots()
                text += self._describe_axes()
                text += self._describe_all_plots()
                text += self._describe_reporting_delay_period()

        return text

    # Introduction

    @classmethod
    def _introduce_no_plots(cls) -> str:
        return "There is no data being shown for this chart."

    @classmethod
    def _introduce_single_plot(cls) -> str:
        return "There is only 1 plot on this chart. "

    def _introduce_multiple_plots(self) -> str:
        return f"There are {len(self.plots_data)} plots on this chart. "

    # Axes

    def _describe_axes(self) -> str:
        plot_parameters: PlotParameters = self.plots_data[0].parameters
        return (
            f"The horizontal X-axis is labelled '{plot_parameters.x_axis}'. "
            f"Whilst the vertical Y-axis is labelled '{plot_parameters.y_axis}'. "
        )

    # Description for single plot chart

    def _describe_only_plot(self) -> str:
        """Builds a description of a plot. Assumes there is only 1 plot on the chart.

        Notes:
            This will include content about the colour of the plot.
            If the plot was given a `label`,
            then commentary will be made regarding this.
            And if the plot is date-based i.e. has date along the x-axis
            then the description will include content about the data itself.

        Returns:
            String representation of the plot.
            Describing its parameters and its data if valid.

        """
        plot_data: PlotData = self.plots_data[0]
        plot_parameters: PlotParameters = plot_data.parameters

        description: str = self._describe_plot_type(plot_parameters=plot_parameters)

        if plot_parameters.label:
            description += f"The plot has a label of '{plot_parameters.label}'. "

        description += self._describe_plot_parameters(plot_parameters=plot_parameters)

        if self._plot_is_headline_data(plot_data=plot_data):
            description += self._describe_headline_plot_data(plot_data=plot_data)

        elif self._plot_is_date_based_timeseries_data(plot_data=plot_data):
            with contextlib.suppress(Exception):
                description += self._describe_date_based_plot_data(plot_data=plot_data)

        return description

    # Description for multiple plot chart

    def _describe_all_plots(self) -> str:
        """Builds a description of each plot. Assumes there are multiple plots on the chart.

        Notes:
            This will include content about the colour of each plot.
            If plots were given a `label`,
            then commentary will be made regarding this.
            And if any plots are date-based i.e. have date along the x-axis
            then the description will include content about the data itself.

        Returns:
            String representation of each plot in the chart.
            This will describe the parameters of each plot
            along with the data if the plots are date-based.

        """
        description = ""
        for index, plot_data in enumerate(self.plots_data, 1):
            description += self._describe_next_plot_in_multiple_plot_group(
                index=index, plot_data=plot_data
            )
        return description

    def _describe_next_plot_in_multiple_plot_group(
        self, *, index: int, plot_data: PlotData
    ) -> str:
        """Builds a description of a plot. Assumes there are multiple plots on the chart.

        Notes:
            This will include content about the colour of the plot.
            If the plot was given a `label`,
            then commentary will be made regarding this.
            And if the plot is date-based i.e. has date along the x-axis
            then the description will include content about the data itself.

        Args:
            index: The plot number i.e. if the current plot
                was the 2nd plot, the index would be 2.
            plot_data:
                An enrich `PlotData` model containing
                all the parameters and associated data
                which is used to create the plot.

        Returns:
            String representation of the plot.
            Describing its parameters and its data if valid.

        """
        plot_parameters = plot_data.parameters
        description = f"This is plot number {index} on this chart. "
        description += self._describe_plot_type(plot_parameters=plot_parameters)

        if plot_parameters.label:
            description += f"The plot has a label of '{plot_parameters.label}'. "

        description += self._describe_plot_parameters(plot_parameters=plot_parameters)

        if self._plot_is_headline_data(plot_data=plot_data):
            with contextlib.suppress(Exception):
                description += self._describe_headline_plot_data(plot_data=plot_data)

        elif self._plot_is_date_based_timeseries_data(plot_data=plot_data):
            with contextlib.suppress(Exception):
                description += self._describe_date_based_plot_data(plot_data=plot_data)

        return description

    # Data description

    @classmethod
    def _describe_headline_plot_data(cls, *, plot_data: PlotData) -> str:
        """Builds a description of the data for the given headline data plot.

        Args:
            plot_data:
                An enrich `PlotData` model containing
                all the parameters and associated data
                which is used to create the plot.

        Returns:
            String representation of the plot

        """
        return (
            f"This plot shows `{plot_data.x_axis_values[0]}` along the X-axis. "
            f"And `{plot_data.y_axis_values[0]}` along the Y-axis. "
        )

    def _describe_date_based_plot_data(
        self, *, plot_data: PlotData, number_of_parts: int = 6
    ) -> str:
        """Builds a description of the data for the given plot. Assumes the plot uses `date` along the x-axis

        Notes:
            The data is split into N parts as dictated by the
            `number_of_parts` parameter.
            The commentary is created about each individual
            section of data, relating to the overall rise/fall
            between the start and end of each section.

        Args:
            plot_data:
                An enrich `PlotData` model containing
                all the parameters and associated data
                which is used to create the plot.
            number_of_parts: The number of sections
                to split the data into.
                Whereby each section then has commentary
                created for it.

        Returns:
            String representation of the plot.
            Describing its data and the rise/fall
            between each section in the plot

        """
        overall_start_date: str = self._stringify_date(
            date_obj=plot_data.x_axis_values[0]
        )
        overall_end_date: str = self._stringify_date(
            date_obj=plot_data.x_axis_values[-1]
        )
        description = (
            f"This plot shows data from {overall_start_date} to {overall_end_date}. "
        )

        date_parts: Iterator[list[datetime.date]] = split_into_n_parts(
            data=plot_data.x_axis_values, n=number_of_parts
        )
        metric_value_parts: Iterator[list[Decimal]] = split_into_n_parts(
            data=plot_data.y_axis_values, n=number_of_parts
        )

        for index, metric_value_part in enumerate(metric_value_parts, 1):
            date_part: list[datetime.date] = next(date_parts)
            try:
                section_description: str = self._build_description_for_section_of_data(
                    metric_value_part=metric_value_part,
                    date_part=date_part,
                    index=index,
                    number_of_parts=number_of_parts,
                )
            except IndexError:
                continue

            description += section_description

        return description

    def _build_description_for_section_of_data(
        self,
        *,
        metric_value_part: list[Decimal],
        date_part: list[datetime.date],
        index: int,
        number_of_parts: int,
    ) -> str:
        """Builds a description of the individual part with the metric and date values

        Args:
            metric_value_part: List of `Decimal` values
                representing the data points within the data section
            date_part: List of `date` objects which represent the
                data points within the data section
            index: The current part number
                i.e. if the current part was the 2nd section of data,
                then the index would be 2
            number_of_parts: The number of sections
                which the data is being split into.

        Returns:
            A generator of `n` items, whereby
            each item is a sublist of the original `data`

        """
        start_value: float = self._stringify_metric_value(
            metric_value=metric_value_part[0]
        )
        end_value: float = self._stringify_metric_value(
            metric_value=metric_value_part[-1]
        )
        start_date: str = self._stringify_date(date_obj=date_part[0])
        end_date: str = self._stringify_date(date_obj=date_part[-1])

        if end_value > start_value:
            part_description = f"It rose from {start_value} on {start_date} to {end_value} on {end_date}. "
        elif end_value == start_value:
            part_description = (
                f"The date fluctuates between {start_value} on {start_date}, "
                f"ending with the same value on {end_date}. "
            )
        else:
            part_description = f"It fell from {start_value} on {start_date} to {end_value} on {end_date}. "

        if index == number_of_parts:
            part_description = f"And finally. {part_description}"

        return part_description

    # Utilities

    @classmethod
    def _stringify_chart_type(cls, *, plot_parameters: PlotData) -> str:
        chart_type: str = plot_parameters.chart_type
        match chart_type:
            case ChartTypes.bar.value:
                return "bar"
            case ChartTypes.line_multi_coloured.value:
                return "line"
            case ChartTypes.line_with_shaded_section.value:
                return "line"

    def _describe_plot_type(self, *, plot_parameters: PlotParameters) -> str:
        line_type: str = self._get_line_type_or_default(plot_parameters=plot_parameters)
        line_colour: str = self._get_line_colour_or_default(
            plot_parameters=plot_parameters
        )
        plot_type: str = self._stringify_chart_type(plot_parameters=plot_parameters)

        return f"This is a {line_colour} {line_type} {plot_type} plot. "

    @classmethod
    def _stringify_sex(cls, *, plot: PlotParameters) -> str:
        match plot.sex:
            case "f":
                return "females"
            case "m":
                return "males"
            case _:
                return "all"

    def _describe_plot_parameters(self, *, plot_parameters: PlotParameters) -> str:
        sex_grouping: str = self._stringify_sex(plot=plot_parameters)
        return (
            f"This plot shows data for {plot_parameters.topic}. "
            f"Specifically the metric '{plot_parameters.metric}' for the {plot_parameters.geography} area, "
            f"along with the age banding of '{plot_parameters.age}' for the gender group of {sex_grouping}. "
        )

    @classmethod
    def _get_line_colour_or_default(cls, *, plot_parameters: PlotParameters) -> str:
        if plot_parameters.line_colour:
            return plot_parameters.line_colour.lower()

        if plot_parameters.chart_type == ChartTypes.bar.value:
            return RGBAChartLineColours.BLUE.name.lower()

        return RGBAChartLineColours.BLACK.name.lower()

    @classmethod
    def _get_line_type_or_default(cls, *, plot_parameters: PlotParameters) -> str:
        if plot_parameters.line_type:
            return plot_parameters.line_type.lower()

        return ChartLineTypes.SOLID.value.lower()

    @classmethod
    def _stringify_date(cls, *, date_obj: datetime.date) -> str:
        return date_obj.strftime(format=READABLE_DATE_FORMAT)

    @classmethod
    def _stringify_metric_value(cls, metric_value: Decimal) -> float:
        try:
            return float(metric_value.normalize())
        except AttributeError:
            return float(metric_value)

    @classmethod
    def _plot_is_date_based_timeseries_data(cls, *, plot_data: PlotData) -> bool:
        return type(plot_data.x_axis_values[0]) is datetime.date

    @classmethod
    def _plot_is_headline_data(cls, *, plot_data: PlotData) -> bool:
        return plot_data.parameters.is_headline_data

    def _describe_reporting_delay_period(self) -> str:
        try:
            start_of_reporting_delay_period: datetime.date = (
                get_x_value_at_start_of_reporting_delay_period(
                    chart_plots_data=self.plots_data
                )
            )
        except (
            NoReportingDelayPeriodFoundError,
            ReportingDelayNotProvidedToPlotsError,
        ):
            return "There is no reporting delay period being tracked for the data on this chart. "

        return (
            f"Data from {self._stringify_date(date_obj=start_of_reporting_delay_period)} onwards "
            f"falls under the reporting delay period. "
            f"This means those figures are still subject to retrospective updates "
            f"and should therefore not be considered to be final. "
        )


def split_into_n_parts(*, data: list[Any], n: int) -> Iterator[list[Any]]:
    """Splits the given `data` into `n` number of parts

    Args:
        data: The overarching list to be broken up
        n: The number of parts to split the list into

    Returns:
        A generator of `n` items, whereby
        each item is a sublist of the original `data`

    """
    quotient, remainder = divmod(len(data), n)

    return (
        data[
            part_number * quotient
            + min(part_number, remainder) : (part_number + 1) * quotient
            + min(part_number + 1, remainder)
        ]
        for part_number in range(n)
    )
