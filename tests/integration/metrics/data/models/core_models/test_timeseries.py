import datetime

import django.db.utils
import pytest

from metrics.data.models.core_models import CoreTimeSeries
from tests.factories.metrics.time_series import CoreTimeSeriesFactory


class TestCoreTimeSeries:
    @pytest.mark.django_db
    def test_models_remain_unique_for_updated_refresh_dates_with_no_functional_change(
        self,
    ):
        """
        Given an existing `CoreTimeSeries` record
        When another record is attempted to be created with a new `refresh_date` only
        Then an `IntegrityError` is raised
        And the existing version of the `CoreTimeSeries` record
            maintains the original `refresh_date` without overwriting it
        """
        # Given
        date = datetime.date.today()
        original_refresh_date = datetime.datetime(year=2023, month=10, day=19)
        original_record = CoreTimeSeriesFactory.create_record(
            metric_value=123, date=date, refresh_date=original_refresh_date
        )

        # When / Then
        subsequent_refresh_date = datetime.datetime(year=2023, month=10, day=26)
        with pytest.raises(django.db.utils.IntegrityError):
            CoreTimeSeriesFactory.create_record(
                metric_value=123, date=date, refresh_date=subsequent_refresh_date
            )

            # Check that there is only 1 'version' of that data
            assert CoreTimeSeries.objects.count() == 1
            # Check that the `refresh_date` is not overwritten
            # and remains as the original `refresh_date`
            assert (
                CoreTimeSeries.objects.first().refresh_date
                == original_record.original_refresh_date
                != subsequent_refresh_date
            )

    @pytest.mark.django_db
    def test_models_allows_new_record_with_new_metric_value_and_refresh_date(self):
        """
        Given an existing `CoreTimeSeries` record
        When another record is attempted to be created for that same `date`
            which contains a new `metric_value` and `refresh_date`
        Then the record will be created successfully
        """
        # Given
        date = datetime.date.today()
        original_metric_value = 123
        original_refresh_date = datetime.datetime(year=2023, month=10, day=19)
        CoreTimeSeriesFactory.create_record(
            metric_value=original_metric_value,
            date=date,
            refresh_date=original_refresh_date,
        )

        # When
        subsequent_refresh_date = datetime.datetime(year=2023, month=10, day=26)
        CoreTimeSeriesFactory.create_record(
            metric_value=original_metric_value + 1,
            date=date,
            refresh_date=subsequent_refresh_date,
        )

        # Then
        # Check that there are now 2 'versions' of that data
        assert CoreTimeSeries.objects.count() == 2

    @pytest.mark.django_db
    def test_allows_new_record_with_updated_reporting_delay_period(self):
        """
        Given an existing `CoreTimeSeries` record
        When another record is attempted to be created for that same `date`
            which contains a new `in_reporting_delay_period` value
        Then the record will be created successfully
        """
        # Given
        date = datetime.date.today()
        original_metric_value = 123
        original_refresh_date = datetime.datetime(year=2023, month=10, day=19)
        CoreTimeSeriesFactory.create_record(
            metric_value=original_metric_value,
            date=date,
            refresh_date=original_refresh_date,
            in_reporting_delay_period=True,
        )

        # When
        subsequent_refresh_date = datetime.datetime(year=2023, month=10, day=26)
        CoreTimeSeriesFactory.create_record(
            metric_value=original_metric_value,
            date=date,
            refresh_date=subsequent_refresh_date,
            in_reporting_delay_period=False,
        )

        # Then
        # Check that there are now 2 'versions' of that data
        assert CoreTimeSeries.objects.count() == 2

    @pytest.mark.django_db
    def test_can_set_is_public_to_false(self):
        """
        Given a `CoreTimeSeries` record
        When `is_public` is explicitly set to `False`
        Then the value should be stored correctly in the database
        """
        # Given / When
        record = CoreTimeSeriesFactory.create_record(is_public=False)
        # Then
        assert record.is_public is False
