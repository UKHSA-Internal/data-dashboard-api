from metrics.data.models.api_models import APITimeSeries


class MetricsPublicAPIInterface:
    @classmethod
    def get_api_timeseries_model(cls) -> APITimeSeries:
        return APITimeSeries
