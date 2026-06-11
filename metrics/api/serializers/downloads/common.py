from rest_framework import serializers

from metrics.api.serializers import help_texts
from metrics.domain.common.utils import (
    ChartAxisFields,
)

FILE_FORMAT_CHOICES: list[str] = ["json", "csv"]


class BaseDownloadsSerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(
        choices=FILE_FORMAT_CHOICES,
        required=True,
        help_text=help_texts.FILE_DOWNLOAD_FORMAT,
    )
    x_axis = serializers.ChoiceField(
        choices=ChartAxisFields.choices(),
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=help_texts.CHART_X_AXIS,
    )
    y_axis = serializers.ChoiceField(
        choices=ChartAxisFields.choices(),
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=help_texts.CHART_Y_AXIS,
    )


class BulkDownloadsSerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(
        choices=FILE_FORMAT_CHOICES,
        required=True,
        help_text=help_texts.FILE_DOWNLOAD_FORMAT,
    )
