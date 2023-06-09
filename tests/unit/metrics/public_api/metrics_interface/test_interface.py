from metrics.data.models.api_models import APITimeSeries
from metrics.public_api.metrics_interface.interface import MetricsPublicAPIInterface


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
