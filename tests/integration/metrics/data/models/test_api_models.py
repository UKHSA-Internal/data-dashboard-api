import datetime

import django.db.utils
import pytest

from metrics.data.models.api_models import APITimeSeries
from tests.factories.metrics.api_models.time_series import APITimeSeriesFactory


class TestAPITimeSeries:
    @pytest.mark.django_db
    def test_models_remain_unique_for_updated_refresh_dates_with_no_functional_change(
        self,
    ):
        """
        Given an existing `APITimeSeries` record
        When another record is attempted to be created with a new `refresh_date` only
        Then an `IntegrityError` is raised
        And the existing version of the `APITimeSeries` record
            maintains the original `refresh_date` without overwriting it
        """
        # Given
        date = datetime.date.today()
        original_refresh_date = datetime.datetime(year=2023, month=10, day=19)
        original_record = APITimeSeriesFactory.create_record(
            metric_value=123, date=date, refresh_date=original_refresh_date
        )

        # When / Then
        subsequent_refresh_date = datetime.datetime(year=2023, month=10, day=26)
        with pytest.raises(django.db.utils.IntegrityError):
            APITimeSeriesFactory.create_record(
                metric_value=123, date=date, refresh_date=subsequent_refresh_date
            )

            # Check that there is only 1 'version' of that data
            assert APITimeSeries.objects.count() == 1
            # Check that the `refresh_date` is not overwritten
            # and remains as the original `refresh_date`
            assert (
                APITimeSeries.objects.first().refresh_date
                == original_record.original_refresh_date
                != subsequent_refresh_date
            )

    @pytest.mark.django_db
    def test_models_allows_new_record_with_new_metric_value_and_refresh_date(self):
        """
        Given an existing `APITimeSeries` record
        When another record is attempted to be created for that same `date`
            which contains a new `metric_value` and `refresh_date`
        Then the record will be created successfully
        """
        # Given
        date = datetime.date.today()
        original_metric_value = 123
        original_refresh_date = datetime.datetime(year=2023, month=10, day=19)
        APITimeSeriesFactory.create_record(
            metric_value=original_metric_value,
            date=date,
            refresh_date=original_refresh_date,
        )

        # When / Then
        subsequent_refresh_date = datetime.datetime(year=2023, month=10, day=26)
        APITimeSeriesFactory.create_record(
            metric_value=original_metric_value + 1,
            date=date,
            refresh_date=subsequent_refresh_date,
        )

        # Check that there are now 2 'versions' of that data
        assert APITimeSeries.objects.count() == 2

    @pytest.mark.django_db
    def test_allows_new_record_with_updated_reporting_lag_period(self):
        """
        Given an existing `APITimeSeries` record
        When another record is attempted to be created for that same `date`
            which contains a new `in_reporting_lag_period` value
        Then the record will be created successfully
        """
        # Given
        date = datetime.date.today()
        metric_value = 123
        original_refresh_date = datetime.datetime(year=2023, month=10, day=19)
        APITimeSeriesFactory.create_record(
            metric_value=metric_value,
            date=date,
            refresh_date=original_refresh_date,
            in_reporting_lag_period=True,
        )

        # When
        subsequent_refresh_date = datetime.datetime(year=2023, month=10, day=26)
        APITimeSeriesFactory.create_record(
            metric_value=metric_value,
            date=date,
            refresh_date=subsequent_refresh_date,
            in_reporting_lag_period=False,
        )

        # Then
        # Check that there are now 2 'versions' of that data
        assert APITimeSeries.objects.count() == 2
