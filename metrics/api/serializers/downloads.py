from typing import List

from rest_framework import serializers

from metrics.api.serializers import help_texts

FILE_FORMAT_CHOICES: List[str] = ["json", "csv"]


class DownloadsQuerySerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(
        choices=FILE_FORMAT_CHOICES,
        required=True,
        help_text=help_texts.FILE_DOWNLOAD_FORMAT,
    )


class DownloadPlotSerializer(serializers.Serializer):
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
    stratum = serializers.CharField(
        required=False,
        help_text=help_texts.STRATUM_FIELD,
        allow_blank=True,
        default="",
    )
    geography = serializers.CharField(
        required=False,
        help_text=help_texts.GEOGRAPHY_FIELD,
        allow_blank=True,
        default="",
    )
    geography_type = serializers.CharField(
        required=False,
        help_text=help_texts.GEOGRAPHY_TYPE_FIELD,
        allow_blank=True,
        default="",
    )
    date_from = serializers.DateField(
        help_text=help_texts.DATE_FROM_FIELD,
        required=False,
        default="",
        allow_null=True,
    )
    date_to = serializers.DateField(
        help_text=help_texts.DATE_FROM_FIELD,
        required=False,
        default="",
        allow_null=True,
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
