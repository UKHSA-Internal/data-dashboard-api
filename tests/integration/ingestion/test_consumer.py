import copy
import zoneinfo

import pytest

from ingestion.consumer import Consumer
from ingestion.utils.type_hints import INCOMING_DATA_TYPE
from metrics.data.enums import TimePeriod
from metrics.data.models.core_models import (
    Age,
    CoreHeadline,
    CoreTimeSeries,
    Geography,
    GeographyType,
    Metric,
    MetricGroup,
    SubTheme,
    Theme,
    Topic,
)

EXPECTED_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
EXPECTED_DATE_FORMAT = "%Y-%m-%d"


class TestConsumer:
    @pytest.mark.django_db
    def test_can_ingest_headline_data_successfully(
        self, example_headline_data: INCOMING_DATA_TYPE
    ):
        """
        Given an example headline data file
        When `create_core_headlines()` is called
            from an instance of `Consumer`
        Then `CoreHeadline` records are created with the correct values
        """
        # Given
        consumer = Consumer(source_data=example_headline_data)
        assert not CoreHeadline.objects.exists()

        # When
        consumer.create_core_headlines()

        # Then
        # Check that 1 `CoreHeadline` record is created per row of data
        assert CoreHeadline.objects.all().count() == len(example_headline_data["data"])

        # Check the first `CoreHeadline` record was set
        # with the values from the first object in the original JSON
        core_headline_one = CoreHeadline.objects.first()
        self._assert_core_headline_model_has_correct_values(
            core_headline=CoreHeadline.objects.first(),
            main_headline_data=example_headline_data,
            headline_specific_data=example_headline_data["data"][0],
        )

        # Check the second `CoreHeadline` record was set
        # with the correct corresponding the values as above
        core_headline_two = CoreHeadline.objects.last()
        self._assert_core_headline_model_has_correct_values(
            core_headline=CoreHeadline.objects.last(),
            main_headline_data=example_headline_data,
            headline_specific_data=example_headline_data["data"][1],
        )

        # Check that the 2 `CoreHeadline` records which are closely related
        # share the same supporting models
        # i.e. They should share the same `Theme`, `SubTheme` & `Topic` etc
        self._assert_share_same_supporting_models(
            first_record=core_headline_one,
            second_record=core_headline_two,
        )

        # Check that only 1 core supporting model is
        # created where necessary for each value
        assert Theme.objects.count() == 1
        assert SubTheme.objects.count() == 1
        assert Topic.objects.count() == 1
        assert Metric.objects.count() == 1
        assert MetricGroup.objects.count() == 1
        assert Age.objects.count() == 1
        assert GeographyType.objects.count() == 1
        assert Geography.objects.count() == 1

    @pytest.mark.django_db
    def test_can_ingest_timeseries_data_successfully(
        self, example_time_series_data: INCOMING_DATA_TYPE
    ):
        """
        Given an example headline data file
        When `create_core_time_series()` is called
            from an instance of `Consumer`
        Then `CoreTimeSeries` records are created with the correct values
        """
        # Given
        consumer = Consumer(source_data=example_time_series_data)
        assert CoreTimeSeries.objects.all().count() == 0

        # When
        consumer.create_core_time_series()

        # Then
        # Check that 1 `CoreTimeSeries` record is created per row of data
        assert CoreTimeSeries.objects.all().count() == len(
            example_time_series_data["time_series"]
        )

        # Check the first `CoreTimeSeries` record was set
        # with the values from the first object in the original JSON
        core_timeseries_one = CoreTimeSeries.objects.first()
        self._assert_core_timeseries_model_has_correct_values(
            core_timeseries=core_timeseries_one,
            main_timeseries_data=example_time_series_data,
            timeseries_specific_data=example_time_series_data["time_series"][0],
        )

        # Check the second `CoreTimeSeries` record was set
        # with the correct corresponding the values as above
        core_timeseries_two = CoreTimeSeries.objects.last()
        self._assert_core_timeseries_model_has_correct_values(
            core_timeseries=core_timeseries_two,
            main_timeseries_data=example_time_series_data,
            timeseries_specific_data=example_time_series_data["time_series"][1],
        )

        # Check that the 2 `CoreTimeSeries` records which are closely related
        # share the same supporting models
        # i.e. They should share the same `Theme`, `SubTheme` & `Topic` etc
        self._assert_share_same_supporting_models(
            first_record=core_timeseries_one,
            second_record=core_timeseries_two,
        )

        # Check that only 1 core supporting model is
        # created where necessary for each value
        assert Theme.objects.count() == 1
        assert SubTheme.objects.count() == 1
        assert Topic.objects.count() == 1
        assert Metric.objects.count() == 1
        assert MetricGroup.objects.count() == 1
        assert Age.objects.count() == 1
        assert Geography.objects.count() == 1
        assert GeographyType.objects.count() == 1

    @staticmethod
    def _assert_core_model(
        model: CoreHeadline | CoreTimeSeries, source_data: INCOMING_DATA_TYPE
    ):
        assert model.metric.topic.sub_theme.theme.name == source_data["parent_theme"]
        assert model.metric.topic.sub_theme.name == source_data["child_theme"]
        assert model.metric.metric_group.topic.name == source_data["topic"]
        assert model.metric.metric_group.name == source_data["metric_group"]
        assert model.metric.name == source_data["metric"]

        assert model.geography.geography_type.name == source_data["geography_type"]
        assert model.geography.name == source_data["geography"]
        assert model.geography.geography_code == source_data["geography_code"]

        assert model.age.name == source_data["age"]
        assert model.sex == {"all": "all", "female": "f", "male": "m"}.get(
            source_data["sex"].lower()
        )
        assert model.stratum.name == source_data["stratum"]
        assert (
            str(model.refresh_date) == f"{source_data['refresh_date']} 00:00:00+00:00"
        )
        # When the source data provides just a date for the `refresh_date`
        # then we set the `refresh_date` on the model to midnight of that same date

    def _assert_core_headline_model_has_correct_values(
        self,
        core_headline: CoreHeadline,
        main_headline_data: INCOMING_DATA_TYPE,
        headline_specific_data: dict[str, str | float],
    ) -> None:
        self._assert_core_model(model=core_headline, source_data=main_headline_data)
        london_timezone = zoneinfo.ZoneInfo(key="Europe/London")
        assert (
            core_headline.period_start.astimezone(tz=london_timezone).strftime(
                EXPECTED_DATE_FORMAT
            )
            == headline_specific_data["period_start"]
        )
        assert (
            core_headline.period_end.astimezone(tz=london_timezone).strftime(
                EXPECTED_DATE_FORMAT
            )
            == headline_specific_data["period_end"]
        )
        assert (
            str(core_headline.metric_value)
            == f"{headline_specific_data['metric_value']:.4f}"
        )
        assert (
            core_headline.embargo.strftime(EXPECTED_DATETIME_FORMAT)
            == headline_specific_data["embargo"]
        )

    @staticmethod
    def _assert_share_same_supporting_models(
        first_record: CoreHeadline | CoreTimeSeries,
        second_record: CoreHeadline | CoreTimeSeries,
    ) -> None:
        assert first_record.metric == second_record.metric
        assert first_record.metric.metric_group == second_record.metric.metric_group
        assert (
            first_record.metric.metric_group.topic
            == second_record.metric.metric_group.topic
        )
        assert (
            first_record.metric.metric_group.topic.sub_theme
            == second_record.metric.metric_group.topic.sub_theme
        )
        assert (
            first_record.metric.metric_group.topic.sub_theme.theme
            == second_record.metric.metric_group.topic.sub_theme.theme
        )
        assert first_record.age == second_record.age

    def _assert_core_timeseries_model_has_correct_values(
        self,
        core_timeseries: CoreTimeSeries,
        main_timeseries_data: INCOMING_DATA_TYPE,
        timeseries_specific_data: dict[str, str | float],
    ) -> None:
        self._assert_core_model(model=core_timeseries, source_data=main_timeseries_data)
        assert str(core_timeseries.date) == str(timeseries_specific_data["date"])
        assert (
            core_timeseries.metric_frequency
            == TimePeriod[main_timeseries_data["metric_frequency"].title()].value
        )
        year, month, _ = timeseries_specific_data["date"].split("-")
        assert str(core_timeseries.year) == year
        assert str(core_timeseries.month) == month
        assert str(core_timeseries.epiweek) == str(timeseries_specific_data["epiweek"])

    @pytest.mark.django_db
    def test_can_ingest_duplicated_data_with_force_write_flag(self):
        """
        Given an original core time series
        And 2 further updates, the 1st of which sets a new value
            whilst the last update resets the original value
        When `create_core_time_series()` is called
            from an instance of `Consumer`
        Then `CoreTimeSeries` records are created with the correct values
        And the final update can be written with the `force_write` flag
        """
        # Given
        original_source_data = {
            "parent_theme": "infectious_disease",
            "child_theme": "vaccine_preventable",
            "topic": "Measles",
            "metric_group": "cases",
            "metric": "measles_cases_casesByOnsetWeek",
            "geography_type": "Nation",
            "geography": "England",
            "geography_code": "E92000001",
            "age": "all",
            "sex": "all",
            "stratum": "default",
            "metric_frequency": "weekly",
            "refresh_date": "2024-07-16 08:00:00",
            "time_series": [
                {
                    "epiweek": 25,
                    "date": "2024-06-17",
                    "metric_value": 71,
                    "embargo": "2024-07-16 09:30:00",
                    "is_public": True
                }
            ],
        }

        consumer = Consumer(source_data=original_source_data)
        assert CoreTimeSeries.objects.all().count() == 0

        # When
        consumer.create_core_time_series()

        # Then
        # Check that the 1st `CoreTimeSeries` record is created
        core_timeseries_one = CoreTimeSeries.objects.last()
        original_metric_value = original_source_data["time_series"][0]["metric_value"]
        assert str(core_timeseries_one.metric_value) == f"{original_metric_value:.4f}"

        # When
        # Ingest the 2nd record with a completely new `metric_value`
        second_data_with_new_metric_value = copy.deepcopy(original_source_data)
        second_data_with_new_metric_value["time_series"][0]["metric_value"] = 74
        second_data_with_new_metric_value["refresh_date"] = "2024-07-23 08:00:00"
        consumer = Consumer(source_data=second_data_with_new_metric_value)
        consumer.create_core_time_series()

        # Then
        assert CoreTimeSeries.objects.count() == 2
        core_timeseries_two = CoreTimeSeries.objects.last()
        updated_metric_value = second_data_with_new_metric_value["time_series"][0][
            "metric_value"
        ]
        assert str(core_timeseries_two.metric_value) == f"{updated_metric_value:.4f}"

        # When
        # Ingest the last record which resets the `metric_value` to the original value
        final_data_with_reset_metric_value = copy.deepcopy(original_source_data)
        final_data_with_reset_metric_value["refresh_date"] = "2024-07-30 08:00:00"
        final_data_with_reset_metric_value["time_series"][0]["force_write"] = True
        consumer = Consumer(source_data=final_data_with_reset_metric_value)
        consumer.create_core_time_series()

        # Then
        assert CoreTimeSeries.objects.count() == 3
        core_timeseries_final = CoreTimeSeries.objects.last()
        assert str(core_timeseries_final.metric_value) == f"{original_metric_value:.4f}"
