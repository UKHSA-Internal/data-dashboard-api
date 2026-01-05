from collections.abc import Iterable
from decimal import Decimal
from typing import Literal

from pydantic.main import BaseModel
from rest_framework.request import Request

from metrics.domain.models import ChartRequestParams
from metrics.domain.models.plots import PlotParameters

OPTIONAL_STRING = str | None


class Subplots(BaseModel):
    subplot_title: str
    x_axis: str
    y_axis: str
    plots: list[PlotParameters]
    request: Request | None = None
    confidence_intervals: bool | None = False
    confidence_colour: str | None = ""

    class Config:
        arbitrary_types_allowed = True

    @property
    def rbac_permissions(self) -> Iterable["RBACPermission"]:
        return getattr(self.request, "rbac_permissions", [])


"""
This collection of models are the model definitions for a `Request` for a subplot chart.
"""


class SubplotChartRequestParameters(BaseModel):
    file_format: Literal["png", "svg", "jpg", "jpeg", "json", "csv"]
    chart_width: int
    chart_height: int
    x_axis_title: OPTIONAL_STRING = ""
    y_axis_title: OPTIONAL_STRING = ""
    y_axis_minimum_value: Decimal | int | None = 0
    y_axis_maximum_value: Decimal | int | None = None
    target_threshold: float | None = None
    target_threshold_label: str | None = ""
    request: Request | None = None

    subplots: list[Subplots]

    class Config:
        arbitrary_types_allowed = True

    def _extract_all_distinct_group_values(
        self, attribute_to_group_by: str
    ) -> list[str]:
        group_values: list[str] = []
        for subplot in self.subplots:
            for plot in subplot.plots:
                # Note this currently does not work for `x_axis = "date"`
                value = getattr(plot, attribute_to_group_by, None)
                if value and value not in group_values:
                    group_values.append(value)
        return group_values

    @classmethod
    def _get_matching_plot_for_group(
        cls, subplot: Subplots, attribute_to_group_by: str, group_value: str
    ) -> PlotParameters:
        # Find the plot in this subplot matching the current group value
        matching_plot_for_group_value = next(
            plot
            for plot in subplot.plots
            if getattr(plot, attribute_to_group_by, None) == group_value
        )

        return matching_plot_for_group_value.model_copy(
            update={"label": subplot.subplot_title}
        )

    def output_payload_for_tables(self) -> list[ChartRequestParams]:
        """Flip subplot structure into groups of `ChartRequestParams` as dictated by the `x_axis` value

        Notes:
            For example if `x_axis` == "geography", and subplots each contain plots for
            England, North East, Darlington.
            Then this will return 3 `ChartRequestParams`, 1 per geography.
            Each will contain plots for each of the original subplot,
            with the plot label set to the subplot title so that
            table output labels match subplot names.

        Returns:
            List of enriched `ChartRequestParams` objects.

        """
        overall_payload: list[ChartRequestParams] = []

        # Determine the attribute to group by from the first subplot's x_axis
        attribute_to_group_subplots_by: str = self.subplots[0].x_axis

        # Collect distinct group values in a stable order across all subplots
        distinct_group_values: list[str] = self._extract_all_distinct_group_values(
            attribute_to_group_by=attribute_to_group_subplots_by
        )

        # Build a ChartRequestParams per group value
        # E.g. if we've selected the `x_axis` as `"geography"`
        # Then we'll expect 1 group value per distinct geography
        for group_value in distinct_group_values:
            grouped_plots: list[PlotParameters] = []

            for subplot in self.subplots:
                try:
                    matched_plot: PlotParameters = self._get_matching_plot_for_group(
                        subplot=subplot,
                        attribute_to_group_by=attribute_to_group_subplots_by,
                        group_value=group_value,
                    )
                except StopIteration:
                    continue

                grouped_plots.append(matched_plot)

            grouped_subplot = ChartRequestParams(
                metric_group=grouped_plots[0].metric_group,
                plots=grouped_plots,
                file_format=self.file_format,
                chart_height=self.chart_height,
                chart_width=self.chart_width,
                x_axis=self.subplots[0].x_axis,
                y_axis=self.subplots[0].y_axis,
                x_axis_title=self.x_axis_title,
                y_axis_title=self.y_axis_title,
                y_axis_minimum_value=self.y_axis_minimum_value,
                y_axis_maximum_value=self.y_axis_maximum_value,
                request=self.request,
            )

            overall_payload.append(grouped_subplot)

        return overall_payload
