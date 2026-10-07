import zoneinfo
from copy import deepcopy
from dataclasses import dataclass
from unittest import mock

import pytest

from ingestion.file_ingestion import data_ingester
from ingestion.utils import type_hints
from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries
from validation.is_public import (
    MISSING_IS_PUBLIC_FIELD_ERROR,
)

EXPECTED_DATE_FORMAT = "%Y-%m-%d"


@dataclass
class ConfidenceIntervalScenario:
    """
    Simple helper class to define confidence interval test scenarios.
    """

    upper: float | None
    lower: float | None
    value: float


class TestDataIngester:
    @pytest.mark.django_db
    def test_creates_core_headlines_from_data(
        self,
        example_headline_data: type_hints.INCOMING_DATA_TYPE,
        test_filename: str,
    ):
        """
        Given incoming headline type data
        When `data_ingester()` is called
        Then `CoreHeadline` records are created with the correct values
        """
        # Given
        data = example_headline_data
        assert CoreHeadline.objects.all().count() == 0

        # When
        data_ingester(data=data, filename=test_filename)

        # Then
        # Check that 2 `CoreHeadline` records are created per row of data
        assert CoreHeadline.objects.all().count() == len(example_headline_data["data"])
        core_headline = CoreHeadline.objects.first()

        assert core_headline.metric.topic.sub_theme.theme.name == data["parent_theme"]
        assert core_headline.metric.topic.sub_theme.name == data["child_theme"]
        assert core_headline.metric.topic.name == data["topic"]
        assert core_headline.metric.metric_group.name == data["metric_group"]
        assert core_headline.metric.name == data["metric"]

        assert core_headline.geography.name == data["geography"]
        assert core_headline.geography.geography_code == data["geography_code"]
        assert core_headline.geography.geography_type.name == data["geography_type"]

        assert core_headline.age.name == data["age"]
        assert core_headline.stratum.name == data["stratum"]
        assert core_headline.sex == data["sex"]
        assert core_headline.refresh_date.strftime("%Y-%m-%d") == data["refresh_date"]

        london_timezone = zoneinfo.ZoneInfo(key="Europe/London")
        assert (
            core_headline.period_start.astimezone(tz=london_timezone).strftime(
                EXPECTED_DATE_FORMAT
            )
            == data["data"][0]["period_start"]
        )
        assert (
            core_headline.period_end.astimezone(tz=london_timezone).strftime(
                EXPECTED_DATE_FORMAT
            )
            == data["data"][0]["period_end"]
        )
        assert str(round(core_headline.metric_value, 1)) == str(
            data["data"][0]["metric_value"]
        )
        # The embargo timestamp specifies the point in time up to the second
        assert (
            core_headline.embargo.strftime("%Y-%m-%d %H:%M:%S")
            == data["data"][0]["embargo"]
        )

    @pytest.mark.django_db
    def test_creates_core_time_series_from_data(
        self,
        example_time_series_data: type_hints.INCOMING_DATA_TYPE,
        test_filename: str,
    ):
        """
        Given incoming time series type data
        When `data_ingester()` is called
        Then `CoreTimeSeries` records are created with the correct values
        """
        # Given
        data = example_time_series_data
        assert CoreTimeSeries.objects.all().count() == 0

        # When
        data_ingester(data=data, filename=test_filename)

        # Then
        # Check that 1 `CoreTimeSeries` record is created per row of data
        assert CoreTimeSeries.objects.all().count() == len(
            example_time_series_data["time_series"]
        )
        core_time_series = CoreTimeSeries.objects.first()

        assert (
            core_time_series.metric.topic.sub_theme.theme.name == data["parent_theme"]
        )
        assert core_time_series.metric.topic.sub_theme.name == data["child_theme"]
        assert core_time_series.metric.topic.name == data["topic"]
        assert core_time_series.metric.metric_group.name == data["metric_group"]
        assert core_time_series.metric.name == data["metric"]

        assert core_time_series.geography.name == data["geography"]
        assert core_time_series.geography.geography_code == data["geography_code"]
        assert core_time_series.geography.geography_type.name == data["geography_type"]

        assert core_time_series.age.name == data["age"]
        assert core_time_series.stratum.name == data["stratum"]
        assert core_time_series.sex == data["sex"]
        assert (
            core_time_series.refresh_date.strftime("%Y-%m-%d") == data["refresh_date"]
        )

        assert str(core_time_series.date) == data["time_series"][0]["date"]
        assert round(core_time_series.epiweek, 2) == round(
            data["time_series"][0]["epiweek"], 2
        )
        assert str(round(core_time_series.metric_value, 2)) == str(
            round(data["time_series"][0]["metric_value"], 2)
        )
        # The embargo timestamp specifies the point in time up to the second
        assert (
            core_time_series.embargo.strftime("%Y-%m-%d %H:%M:%S")
            == data["time_series"][0]["embargo"]
        )
        assert core_time_series.in_reporting_delay_period is False

    @pytest.mark.django_db
    def test_creates_api_time_series_from_data(
        self,
        example_time_series_data: type_hints.INCOMING_DATA_TYPE,
        test_filename: str,
    ):
        """
        Given incoming time series type data
        When `data_ingester()` is called
        Then `APITimeSeries` records are created with the correct values
        """
        # Given
        data = example_time_series_data
        assert APITimeSeries.objects.all().count() == 0

        # When
        data_ingester(data=data, filename=test_filename)

        # Then
        # Check that 1 `APITimeSeries` record is created per row of data
        assert APITimeSeries.objects.all().count() == len(
            example_time_series_data["time_series"]
        )
        core_time_series = APITimeSeries.objects.first()

        assert core_time_series.theme == data["parent_theme"]
        assert core_time_series.sub_theme == data["child_theme"]
        assert core_time_series.topic == data["topic"]
        assert core_time_series.metric_group == data["metric_group"]
        assert core_time_series.metric == data["metric"]

        assert core_time_series.geography == data["geography"]
        assert core_time_series.geography_code == data["geography_code"]
        assert core_time_series.geography_type == data["geography_type"]

        assert core_time_series.age == data["age"]
        assert core_time_series.stratum == data["stratum"]
        assert core_time_series.sex == data["sex"]
        assert (
            core_time_series.refresh_date.strftime("%Y-%m-%d") == data["refresh_date"]
        )
        assert (
            core_time_series.date.strftime("%Y-%m-%d") == data["time_series"][0]["date"]
        )
        assert core_time_series.epiweek == data["time_series"][0]["epiweek"]
        assert core_time_series.metric_value == data["time_series"][0]["metric_value"]
        # The embargo timestamp specifies the point in time up to the second
        assert (
            core_time_series.embargo.strftime("%Y-%m-%d %H:%M:%S")
            == data["time_series"][0]["embargo"]
        )

    @pytest.mark.django_db
    @mock.patch("validation.is_public.ALLOW_MISSING_IS_PUBLIC_FIELD", False)
    def test_rejects_time_series_when_is_public_is_missing(
        self,
        example_time_series_data: type_hints.INCOMING_DATA_TYPE,
        test_filename: str,
    ):
        data = deepcopy(example_time_series_data)
        for time_series_data in data["time_series"]:
            time_series_data.pop("is_public")

        with pytest.raises(ValueError) as exc_info:
            data_ingester(data=data, filename=test_filename)

        assert str(exc_info.value) == MISSING_IS_PUBLIC_FIELD_ERROR

        assert CoreTimeSeries.objects.count() == 0
        assert APITimeSeries.objects.count() == 0

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "first, second, expected_count",
        [
            # both stay the same
            (
                ConfidenceIntervalScenario(None, None, 500),
                ConfidenceIntervalScenario(None, None, 500),
                # these headline records are identical but nulls are treated as unique by the constraint so we don't
                # expect an update
                2,
            ),
            (
                ConfidenceIntervalScenario(600, 400, 500),
                ConfidenceIntervalScenario(600, 400, 500),
                # these headline records are identical so we don't expect an update
                1,
            ),
            # both are set
            (
                ConfidenceIntervalScenario(None, None, 500),
                ConfidenceIntervalScenario(600, 400, 500),
                2,
            ),
            # both are removed
            (
                ConfidenceIntervalScenario(600, 400, 500),
                ConfidenceIntervalScenario(None, None, 500),
                2,
            ),
            # both are changed
            (
                ConfidenceIntervalScenario(600, 400, 500),
                ConfidenceIntervalScenario(700, 300, 500),
                2,
            ),
            # lower is changed
            (
                ConfidenceIntervalScenario(600, 400, 500),
                ConfidenceIntervalScenario(600, 300, 500),
                2,
            ),
            # upper is changed
            (
                ConfidenceIntervalScenario(600, 400, 500),
                ConfidenceIntervalScenario(700, 400, 500),
                2,
            ),
            # upper and lower stay the same but metric changes
            (
                ConfidenceIntervalScenario(None, None, 500),
                ConfidenceIntervalScenario(None, None, 501),
                2,
            ),
            (
                ConfidenceIntervalScenario(600, 400, 500),
                ConfidenceIntervalScenario(600, 400, 501),
                2,
            ),
            # everything change
            (
                ConfidenceIntervalScenario(600, 400, 500),
                ConfidenceIntervalScenario(700, 300, 501),
                2,
            ),
        ],
    )
    def test_change_in_confidence_intervals_updates_headline(
        self,
        first: ConfidenceIntervalScenario,
        second: ConfidenceIntervalScenario,
        expected_count: int,
        test_filename: str,
    ):
        """
        Given some ingest headline data without confidence intervals
        When `data_ingester` is called with updates to existing data
        Then the correct `CoreHeadline` records are created / not created
        """
        # given a headline metric
        data_v1 = {
            "parent_theme": "extreme_event",
            "child_theme": "mortality-report",
            "topic": "Heat-mortality",
            "metric_group": "headline",
            "metric": "heat-mortality_headline_total",
            "geography_type": "UKHSA Region",
            "geography": "London",
            "geography_code": "E45000001",
            "age": "all",
            "sex": "all",
            "stratum": "Overall",
            "data": [
                {
                    "period_start": "2025-01-01",
                    "period_end": "2025-05-31",
                    "upper_confidence": first.upper,
                    "lower_confidence": first.lower,
                    "metric_value": first.value,
                    "embargo": None,
                    "is_public": True,
                }
            ],
            "refresh_date": "2026-06-15 12:19:37",
        }

        # data_2 is the same record but with potentially updated metric/upper/lower values
        data_v2 = deepcopy(data_v1)
        data_v2["data"][0]["upper_confidence"] = second.upper
        data_v2["data"][0]["lower_confidence"] = second.lower
        data_v2["data"][0]["metric_value"] = second.value

        # when we ingest the first version of the data
        data_ingester(data=data_v1, filename=test_filename)
        # then there should be one headline row
        assert CoreHeadline.objects.count() == 1
        assert CoreHeadline.objects.first().upper_confidence == first.upper
        assert CoreHeadline.objects.first().lower_confidence == first.lower
        assert CoreHeadline.objects.first().metric_value == first.value

        # when we then update that version with the new version
        data_ingester(data=data_v2, filename=test_filename)
        # then
        assert CoreHeadline.objects.count() == expected_count
        assert CoreHeadline.objects.first().upper_confidence == first.upper
        assert CoreHeadline.objects.first().lower_confidence == first.lower
        assert CoreHeadline.objects.first().metric_value == first.value
        if expected_count == 2:
            assert CoreHeadline.objects.last().upper_confidence == second.upper
            assert CoreHeadline.objects.last().lower_confidence == second.lower
            assert CoreHeadline.objects.last().metric_value == second.value

    @pytest.mark.django_db
    def test_no_change_in_confidence_intervals_is_cleaned_up(
        self,
        test_filename: str,
        example_headline_data: type_hints.INCOMING_DATA_TYPE,
    ):
        """
        Given a headline metric with null confidence intervals
        When the metric is ingested three times in a row without any changes other than the refresh date
        Then two records remain after the three ingestions have happened
        """
        # given a headline metric
        data = example_headline_data
        # fiddle with it, we only want 1 metric and we want to explicitely set the confidence intervals to null
        del data["data"][1]
        data["data"][0]["upper_confidence"] = None
        data["data"][0]["lower_confidence"] = None

        # when we ingest the metric once
        data_ingester(data=data, filename=test_filename)
        # then we expect 1 headline row
        assert CoreHeadline.objects.count() == 1

        # when we push the refresh date out by 1 day and ingest again
        data["refresh_date"] = "2023-11-10"
        data_ingester(data=data, filename=test_filename)
        # then we expect 2, the original above and the "new" headline row. This is because the confidence interval null
        # values are treated as unique by the unique constraint and therefore this is seen as a different metric
        assert CoreHeadline.objects.count() == 2
        assert CoreHeadline.objects.first().refresh_date.day == 9
        assert CoreHeadline.objects.last().refresh_date.day == 10

        # when we push the refresh date out by another day and ingest again
        data["refresh_date"] = "2023-11-11"
        data_ingester(data=data, filename=test_filename)
        # then there shouldn't be another record, only two again. The one we previous one we ingested and the one we
        # just ingested.
        assert CoreHeadline.objects.count() == 2
        assert CoreHeadline.objects.first().refresh_date.day == 10
        assert CoreHeadline.objects.last().refresh_date.day == 11

    @pytest.mark.django_db
    def test_no_change_in_confidence_intervals_is_cleaned_up_even_when_refresh_dates_are_the_same(
        self,
        test_filename: str,
        example_headline_data: type_hints.INCOMING_DATA_TYPE,
    ):
        """
        Given a headline metric with null confidence intervals
        When the metric is ingested three times in a row without any changes (even the refresh date is the same)
        Then two records remain after the three ingestions have happened
        """
        # given a headline metric
        data = example_headline_data
        # fiddle with it, we only want 1 metric and we want to explicitly set the confidence intervals to null
        del data["data"][1]
        data["data"][0]["upper_confidence"] = None
        data["data"][0]["lower_confidence"] = None

        # when we ingest the metric once
        data_ingester(data=data, filename=test_filename)
        # then we expect 1 headline row
        assert CoreHeadline.objects.count() == 1

        # when we ingest it again
        data_ingester(data=data, filename=test_filename)
        # then we expect 2
        assert CoreHeadline.objects.count() == 2

        # when we ingest it again
        data_ingester(data=data, filename=test_filename)
        # then we expect 2
        assert CoreHeadline.objects.count() == 2
