from rest_framework import serializers
from rest_framework.request import Request

from metrics.api.serializers import help_texts, plots
from metrics.api.serializers.downloads.common import BaseDownloadsSerializer
from metrics.domain.common.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DataSourceFileType,
    extract_metric_group_from_metric,
)
from metrics.domain.models import ChartRequestParams


class DownloadPlotSerializer(plots.PlotSerializer):
    # Override these two fields as they are merely optional for this serializer
    topic = serializers.CharField(
        required=False,
        help_text=help_texts.TOPIC_FIELD,
        allow_blank=True,
        default="",
    )
    metric = serializers.CharField(
        required=False,
        help_text=help_texts.METRIC_FIELD,
        allow_blank=True,
        default="",
    )


class DownloadListSerializer(serializers.ListSerializer):
    child = DownloadPlotSerializer()


class SingleCategoryDownloadsSerializer(BaseDownloadsSerializer):
    plots = DownloadListSerializer()
    confidence_intervals = serializers.BooleanField(
        required=False,
        default=False,
        allow_null=True,
        help_text=help_texts.CONFIDENCE_INTERVALS,
    )

    def to_models(self, request: Request) -> ChartRequestParams:
        """Creates a `PlotsCollection` from the download
            request parameters.

        Notes:
            The download endpoint can return chart data for download
            from either `CoreHeadline` or `CoreTimeSeries`.
            The `metric_group` is taken from the metric
            provided in the request. This is used to adapt the model
            returned.

        Returns:
            plots_collection: Instance of `PlotsCollection`
        """
        metric_group = extract_metric_group_from_metric(
            metric=self.data["plots"][0]["metric"]
        )

        for plot in self.data["plots"]:
            plot["chart_type"] = "bar"
            plot["x_axis"] = self.data.get("x_axis") or ""
            plot["y_axis"] = self.data.get("y_axis") or ""

        plots_collection = ChartRequestParams(
            metric_group=metric_group,
            plots=self.data["plots"],
            file_format="svg",
            chart_height=DEFAULT_CHART_HEIGHT,
            chart_width=DEFAULT_CHART_WIDTH,
            x_axis="",
            y_axis="",
            confidence_intervals=self.data.get("confidence_intervals", False),
            request=request,
        )

        if DataSourceFileType[metric_group].is_timeseries:
            for plot in plots_collection.plots:
                plot.override_y_axis_choice_to_none = True

        return plots_collection
