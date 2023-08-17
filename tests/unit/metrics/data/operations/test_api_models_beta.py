from unittest import mock

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import CoreTimeSeries
from metrics.data.operations.api_models_beta import (
    create_api_time_series_from_core_time_series,
)


class TestCreateAPITimeSeriesFromCoreTimeSeries:
    def test_uses_correct_fields_from_core_time_series(self):
        """
        Given a mocked `CoreTimeSeries` object
        When `create_api_time_series_from_core_time_series()` is called
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
        assert api_time_series.age == mocked_time_series.age.name
        assert api_time_series.month == mocked_time_series.month
        assert (
            api_time_series.metric_group == mocked_time_series.metric.metric_group.name
        )
        assert api_time_series.refresh_date == mocked_time_series.refresh_date

    def test_uses_explicit_fields_from_call(self):
        """
        Given a mocked `CoreTimeSeries` object
        And a number of pre-defined fields
        When `create_api_time_series_from_core_time_series()` is called
        Then an `APITimeSeries` object is created with the correct fields
        """
        # Given
        mocked_time_series = mock.Mock(spec=CoreTimeSeries)
        fake_theme = "infectious_disease"
        fake_sub_theme = "respiratory"
        fake_topic = "COVID-19"
        fake_metric = "COVID-19_cases_casesByDay"
        fake_metric_group = "cases"
        fake_metric_frequency = "W"
        fake_refresh_date = "2023-08-03"

        # When
        api_time_series = create_api_time_series_from_core_time_series(
            core_time_series=mocked_time_series,
            theme=fake_theme,
            sub_theme=fake_sub_theme,
            topic=fake_topic,
            metric=fake_metric,
            metric_group=fake_metric_group,
            metric_frequency=fake_metric_frequency,
            refresh_date=fake_refresh_date,
        )

        # Then
        assert isinstance(api_time_series, APITimeSeries)
        assert api_time_series.theme == fake_theme
        assert api_time_series.sub_theme == fake_sub_theme
        assert api_time_series.topic == fake_topic
        assert api_time_series.metric == fake_metric
        assert api_time_series.metric_group == fake_metric_group
        assert api_time_series.metric_frequency == fake_metric_frequency
        assert api_time_series.refresh_date == fake_refresh_date
