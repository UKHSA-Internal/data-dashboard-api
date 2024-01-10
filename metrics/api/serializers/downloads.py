from rest_framework import serializers

from metrics.api.serializers import help_texts, plots
from metrics.domain.models import PlotsCollection
from metrics.domain.utils import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH

FILE_FORMAT_CHOICES: list[str] = ["json", "csv"]


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


class DownloadsSerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(
        choices=FILE_FORMAT_CHOICES,
        required=True,
        help_text=help_texts.FILE_DOWNLOAD_FORMAT,
    )

    plots = DownloadListSerializer()

    def to_models(self) -> PlotsCollection:
        for plot in self.data["plots"]:
            plot["chart_type"] = "bar"

        plots_collection = PlotsCollection(
            plots=self.data["plots"],
            file_format="svg",
            chart_height=DEFAULT_CHART_HEIGHT,
            chart_width=DEFAULT_CHART_WIDTH,
            x_axis="",
            y_axis="",
        )

        for plot in plots_collection.plots:
            plot.override_y_axis_choice_to_none = True

        return plots_collection


class BulkDownloadsSerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(
        choices=FILE_FORMAT_CHOICES,
        required=True,
        help_text=help_texts.FILE_DOWNLOAD_FORMAT,
    )
