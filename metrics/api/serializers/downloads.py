from rest_framework import serializers

from metrics.api.serializers import help_texts, plots

FILE_FORMAT_CHOICES: list[str] = ["json", "csv"]


class DownloadsQuerySerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(
        choices=FILE_FORMAT_CHOICES,
        required=True,
        help_text=help_texts.FILE_DOWNLOAD_FORMAT,
    )


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
