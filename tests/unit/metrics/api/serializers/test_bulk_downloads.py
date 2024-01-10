import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers import BulkDownloadsSerializer


class TestBulkDownloadSerializer:
    @pytest.mark.parametrize("valid_bulk_download_format", ["csv", "json"])
    def test_valid_download_format(self, valid_bulk_download_format: str):
        """
        Given a valid file_format provided as a query parameter
        When `is_valid()` is called from the serializer
        Then true is returned
        """
        # Given
        data = {"file_format": valid_bulk_download_format}
        serializer = BulkDownloadsSerializer(data=data)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    def test_invalid_download_form(self):
        """
        Given an invalid file_format provided as a query_param
        When `is_valid()` is called from the serializer
        Then an `ValidationError` is raised.
        """
        data = {"file_format", "invalid.bulk_downloads_format"}
        serializer = BulkDownloadsSerializer(data=data)

        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
