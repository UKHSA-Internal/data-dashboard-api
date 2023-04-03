import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.views import ChartsQuerySerializer


class TestChartsQuerySerializer:
    @pytest.mark.parametrize("file_format", ["svg", "png", "jpg", "jpeg"])
    def test_valid_file_format(self, file_format: str):
        """
        Given a valid file format passed to a `ChartsQuerySerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        data = {"file_format": file_format}
        serializer = ChartsQuerySerializer(data=data)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    def test_invalid_file_format(self):
        """
        Given an invalid file format passed to a `ChartsQuerySerializer` object
        When `is_valid(raise_exception=True)` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        data = {"file_format": "invalid.file.format"}
        serializer = ChartsQuerySerializer(data=data)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
