from unittest import mock

from metrics.data.models.api_models import APITimeSeries
from public_api.metrics_interface.interface import MetricsPublicAPIInterface


class TestMetricsInterface:
    def test_get_api_timeseries_model_returns_correct_model(self):
        """
        Given the `MetricsPublicAPIInterface` class
        When `get_api_timeseries_model()` is called
        Then the `APITimeSeries` model is returned
        """
        # Given
        metrics_public_api_interface = MetricsPublicAPIInterface

        # When
        api_timeseries_model = metrics_public_api_interface.get_api_timeseries_model()

        # Then
        assert api_timeseries_model is APITimeSeries

    @mock.patch("public_api.metrics_interface.interface.AUTH_ENABLED")
    def test_is_auth_enabled_references_setting_in_metrics_app(
        self, mocked_auth_enabled: mock.MagicMock
    ):
        """
        Given the `MetricsPublicAPIInterface` class
        When `is_auth_enabled()` is called
        Then the `AUTH_ENABLED` setting is referenced
        """
        # Given
        metrics_public_api_interface = MetricsPublicAPIInterface

        # When
        auth_enabled = metrics_public_api_interface.is_auth_enabled()

        # Then
        assert auth_enabled == mocked_auth_enabled
