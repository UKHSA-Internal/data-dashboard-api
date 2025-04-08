from metrics.api.settings.auth import AUTH_ENABLED
from metrics.data.models.api_models import APITimeSeries


class MetricsPublicAPIInterface:
    @classmethod
    def get_api_timeseries_model(cls) -> APITimeSeries:
        return APITimeSeries

    @classmethod
    def is_auth_enabled(cls) -> bool:
        return AUTH_ENABLED
