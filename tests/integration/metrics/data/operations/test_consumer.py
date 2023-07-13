import json

import pytest

from ingestion.consumer import Ingestion
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


class TestIngestion:
    @staticmethod
    def _assert_core_headline_model_has_correct_values(
        core_headline: CoreHeadline, headline_data: dict[str, float]
    ) -> None:
        assert core_headline.metric.metric_group.topic.name == headline_data["topic"]
        assert core_headline.metric.metric_group.name == headline_data["metric_group"]
        assert core_headline.metric.name == headline_data["metric"]
        assert (
            core_headline.geography.geography_type.name
            == headline_data["geography_type"]
        )
        assert core_headline.geography.name == headline_data["geography"]
        assert core_headline.sex == headline_data["sex"]
        assert core_headline.age.name == headline_data["age"]
        assert core_headline.stratum.name == headline_data["stratum"]

        assert str(core_headline.period_start) == headline_data["period_start"]
        assert str(core_headline.period_end) == headline_data["period_end"]
        assert str(core_headline.refresh_date) == headline_data["refresh_date"]

        assert float(core_headline.metric_value) == float(headline_data["metric_value"])

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

    @staticmethod
    def _assert_core_timeseries_model_has_correct_values(
        core_timeseries: CoreTimeSeries, timeseries_data: dict[str, str | float | int]
    ) -> None:
        assert (
            core_timeseries.metric.metric_group.topic.name == timeseries_data["topic"]
        )
        assert (
            core_timeseries.metric.metric_group.name == timeseries_data["metric_group"]
        )
        assert core_timeseries.metric.name == timeseries_data["metric"]
        assert (
            core_timeseries.geography.geography_type.name
            == timeseries_data["geography_type"]
        )
        assert core_timeseries.geography.name == timeseries_data["geography"]
        assert core_timeseries.sex == timeseries_data["sex"]
        assert core_timeseries.age.name == timeseries_data["age"]
        assert core_timeseries.stratum.name == timeseries_data["stratum"]

        assert str(core_timeseries.refresh_date) == timeseries_data["refresh_date"]

        assert float(core_timeseries.metric_value) == float(
            timeseries_data["metric_value"]
        )

    @pytest.mark.django_db
    def test_can_ingest_headline_data_successfully(
        self, example_headline_data_json: list[dict[str, float]]
    ):
        """
        Given an example headline data file
        When `create_headlines()` is called from an instance of `Ingestion`
        Then `CoreHeadline` records are created with the correct values
        """
        # Given
        data = json.dumps(example_headline_data_json)
        ingestion = Ingestion(data=data)
        assert CoreHeadline.objects.all().count() == 0

        # When
        ingestion.create_headlines()

        # Then
        # Check that 1 `CoreHeadline` record is created per row of data
        assert CoreHeadline.objects.all().count() == len(example_headline_data_json)

        # Check the first `CoreHeadline` record was set
        # with the values from the first object in the original JSON
        core_headline_one = CoreHeadline.objects.first()
        self._assert_core_headline_model_has_correct_values(
            core_headline=CoreHeadline.objects.first(),
            headline_data=example_headline_data_json[0],
        )

        # Check the second `CoreHeadline` record was set
        # with the correct corresponding the values as above
        core_headline_two = CoreHeadline.objects.last()
        self._assert_core_headline_model_has_correct_values(
            core_headline=CoreHeadline.objects.last(),
            headline_data=example_headline_data_json[1],
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

        # Check that different core supporting models
        # are created where required
        assert Geography.objects.count() == 2
        assert GeographyType.objects.count() == 2

    @pytest.mark.django_db
    def test_can_ingest_timeseries_data_successfully(
        self, example_timeseries_data_json: list[dict[str, float]]
    ):
        """
        Given an example headline data file
        When `create_timeseries()` is called from an instance of `Ingestion`
        Then `CoreTimeSeries` records are created with the correct values
        """
        # Given
        data = json.dumps(example_timeseries_data_json)
        ingestion = Ingestion(data=data)
        assert CoreTimeSeries.objects.all().count() == 0

        # When
        ingestion.create_timeseries()

        # Then
        # Check that 1 `CoreTimeSeries` record is created per row of data
        assert CoreTimeSeries.objects.all().count() == len(example_timeseries_data_json)

        # Check the first `CoreTimeSeries` record was set
        # with the values from the first object in the original JSON
        core_timeseries_one = CoreTimeSeries.objects.first()
        self._assert_core_timeseries_model_has_correct_values(
            core_timeseries=core_timeseries_one,
            timeseries_data=example_timeseries_data_json[0],
        )

        # Check the second `CoreTimeSeries` record was set
        # with the correct corresponding the values as above
        core_timeseries_two = CoreTimeSeries.objects.last()
        self._assert_core_timeseries_model_has_correct_values(
            core_timeseries=core_timeseries_two,
            timeseries_data=example_timeseries_data_json[1],
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
