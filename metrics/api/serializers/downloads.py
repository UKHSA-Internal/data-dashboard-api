from typing import List

from rest_framework import serializers

from metrics.api.serializers import help_texts
from metrics.api.serializers.charts import ChartPlotsListSerializer

FILE_FORMAT_CHOICES: List[str] = ["json", "csv"]


class DownloadsQuerySerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(
        choices=FILE_FORMAT_CHOICES,
        required=True,
        help_text=help_texts.FILE_DOWNLOAD_FORMAT,
    )


class DownloadsSerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(
        choices=FILE_FORMAT_CHOICES,
        required=True,
        help_text=help_texts.FILE_DOWNLOAD_FORMAT,
    )

    # The available fields will be the same as for the charts
    plots = ChartPlotsListSerializer()
