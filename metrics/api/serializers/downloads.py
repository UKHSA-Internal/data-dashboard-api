from typing import List

from rest_framework import serializers

from metrics.api.serializers import help_texts

DOWNLOAD_FORMAT_CHOICES: List[str] = ["json", "csv"]


class DownloadsSerializer(serializers.Serializer):
    format = serializers.ChoiceField(
        choices=DOWNLOAD_FORMAT_CHOICES,
        required=True,
        help_text=help_texts.DOWNLOAD_FORMAT,
    )
