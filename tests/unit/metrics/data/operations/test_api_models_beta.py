from unittest import mock

import _pytest
import pytest

from metrics.data.managers.api_models.time_series import APITimeSeriesManager
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
        And it takes the correct fields from the `TimeSeries` object
        """
        # Given
        mocked_time_series = mock.Mock(spec=CoreTimeSeries)

        # When
        api_time_series = create_api_time_series_from_core_time_series(
            core_time_series=mocked_time_series
        )

        # Then
        assert isinstance(api_time_series, APITimeSeries)
        assert api_time_series.metric_frequency == mocked_time_series.metric_frequency
        assert (
            api_time_series.theme
            == mocked_time_series.metric.topic.sub_theme.theme.name
        )
        assert (
            api_time_series.sub_theme == mocked_time_series.metric.topic.sub_theme.name
        )
        assert api_time_series.topic == mocked_time_series.metric.topic.name
        assert api_time_series.geography == mocked_time_series.geography.name
        assert (
            api_time_series.geography_code
            == mocked_time_series.geography.geography_code
        )
        assert (
            api_time_series.geography_type
            == mocked_time_series.geography.geography_type.name
        )
        assert api_time_series.metric == mocked_time_series.metric.name
        assert api_time_series.stratum == mocked_time_series.stratum.name
        assert api_time_series.age == mocked_time_series.age

        assert api_time_series.sex == mocked_time_series.sex

        assert api_time_series.year == mocked_time_series.year
        assert api_time_series.month == mocked_time_series.month
        assert api_time_series.epiweek == mocked_time_series.epiweek

        assert api_time_series.date == mocked_time_series.date
        assert api_time_series.metric_value == mocked_time_series.metric_value
        assert (
            api_time_series.metric_group == mocked_time_series.metric.metric_group.name
        )

        assert api_time_series.refresh_date == mocked_time_series.refresh_date
