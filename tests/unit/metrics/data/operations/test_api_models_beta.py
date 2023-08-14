from unittest import mock

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import CoreTimeSeries
from metrics.data.operations.api_models_beta import (
    create_api_time_series_from_core_time_series,
)


class TestCreateAPITimeSeriesFromCoreTimeSeries:
    def test_uses_correct_fields_from_core_time_series(self):
        """
        Given a mocked `TimeSeries` object
        When `api_time_series()` is called
        Then an `APITimeSeries` object is created
        And it takes the new fields from the `CoreTimeSeries` object
        """
        # Given
        mocked_time_series = mock.Mock(spec=CoreTimeSeries)

        # When
        api_time_series = create_api_time_series_from_core_time_series(
            core_time_series=mocked_time_series
        )

        # Then
        assert isinstance(api_time_series, APITimeSeries)
        assert (
            api_time_series.geography_code
            == mocked_time_series.geography.geography_code
        )
        assert api_time_series.age == mocked_time_series.age
        assert api_time_series.month == mocked_time_series.month
        assert (
            api_time_series.metric_group == mocked_time_series.metric.metric_group.name
        )
        assert api_time_series.refresh_date == mocked_time_series.refresh_date
