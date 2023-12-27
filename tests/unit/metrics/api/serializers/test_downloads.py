import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers import DownloadsSerializer


class TestDownloadsSerializer:
    @staticmethod
    def _build_valid_payload() -> dict[str, str | list[dict[str, str]]]:
        requested_file_format = "csv"
        requested_plot = {
            "topic": "COVID-19",
            "metric": "COVID-19_cases_rateRollingMean",
            "age": "all",
            "stratum": "default",
            "sex": "all",
            "geography": "England",
            "geography_type": "Nation",
        }
        return {"file_format": requested_file_format, "plots": [requested_plot]}

    def test_to_models_sets_default_chart_type_when_not_provided(self):
        """
        Given a valid payload which has been serialized
        When `to_models()` is called
            from an instance of the `DownloadsSerializer`
        Then the returned model sets the default chart type
        """
        # Given
        valid_payload = self._build_valid_payload()
        serializer = DownloadsSerializer(data=valid_payload)
        serializer.is_valid(raise_exception=True)

        # When
        plots_collection = serializer.to_models()

        # Then
        for plot in plots_collection.plots:
            assert plot.chart_type == "bar"

    def test_to_models_sets_override_y_axis_choice_to_none_to_true(self):
        """
        Given a valid payload which has been serialized
        When `to_models()` is called
            from an instance of the `DownloadsSerializer`
        Then the returned model sets
            `override_y_axis_choice_to_none` to True
        """
        # Given
        valid_payload = self._build_valid_payload()
        serializer = DownloadsSerializer(data=valid_payload)
        serializer.is_valid(raise_exception=True)

        # When
        plots_collection = serializer.to_models()

        # Then
        for plot in plots_collection.plots:
            assert plot.override_y_axis_choice_to_none

    @pytest.mark.parametrize("valid_download_format", ["csv", "json"])
    def test_valid_download_format(self, valid_download_format: str):
        """
        Given a valid format passed to a `DownloadsSerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        data = self._build_valid_payload()
        data["file_format"] = valid_download_format
        serializer = DownloadsSerializer(data=data)

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
        data = self._build_valid_payload()
        data["file_format"] = "invalid.download.format"
        serializer = DownloadsSerializer(data=data)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
