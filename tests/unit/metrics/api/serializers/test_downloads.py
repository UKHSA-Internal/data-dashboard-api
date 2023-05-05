import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers import DownloadsQuerySerializer


class TestDownloadsSerializer:
    @pytest.mark.parametrize("valid_download_format", ["csv", "json"])
    def test_valid_download_format(self, valid_download_format: str):
        """
        Given a valid format passed to a `DownloadsSerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        data = {"file_format": valid_download_format}
        serializer = DownloadsQuerySerializer(data=data)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    def test_invalid_file_format(self):
        """
        Given an invalid download format passed to a `DownloadsSerializer` object
        When `is_valid(raise_exception=True)` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        data = {"file_format": "invalid.download.format"}
        serializer = DownloadsQuerySerializer(data=data)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
