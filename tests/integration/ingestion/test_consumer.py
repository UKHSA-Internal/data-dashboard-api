import json
from unittest import mock

import pytest

from ingestion.consumer import Consumer
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


class TestConsumer:
    @pytest.mark.django_db
    def test_can_ingest_headline_data_successfully(
        self, example_headline_data: list[dict[str, str | float]]
    ):
        """
        Given an example headline data file
        When `create_headlines()` is called from an instance of `Ingestion`
        Then `CoreHeadline` records are created with the correct values
        """
        # Given
        fake_data = mock.Mock()
        fake_data.readlines.return_value = [json.dumps(example_headline_data)]
        consumer = Consumer(data=fake_data)
        assert CoreHeadline.objects.all().count() == 0

        # When
        consumer.create_headlines()

        # Then
        # Check that 1 `CoreHeadline` record is created per row of data
        assert CoreHeadline.objects.all().count() == len(example_headline_data)

        # Check the first `CoreHeadline` record was set
        # with the values from the first object in the original JSON
        core_headline_one = CoreHeadline.objects.first()
        self._assert_core_headline_model_has_correct_values(
            core_headline=CoreHeadline.objects.first(),
            headline_data=example_headline_data[0],
        )

        # Check the second `CoreHeadline` record was set
        # with the correct corresponding the values as above
        core_headline_two = CoreHeadline.objects.last()
        self._assert_core_headline_model_has_correct_values(
            core_headline=CoreHeadline.objects.last(),
            headline_data=example_headline_data[1],
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

        # Check that different core supporting models
        # are created where required
        assert Geography.objects.count() == 2

    @pytest.mark.django_db
    def test_can_ingest_timeseries_data_successfully(
        self, example_timeseries_data: list[dict[str, str | int | float]]
    ):
        """
        Given an example headline data file
        When `create_timeseries()` is called from an instance of `Ingestion`
        Then `CoreTimeSeries` records are created with the correct values
        """
        # Given
        fake_data = mock.Mock()
        fake_data.readlines.return_value = [json.dumps(example_timeseries_data)]
        consumer = Consumer(data=fake_data)
        assert CoreTimeSeries.objects.all().count() == 0

        # When
        consumer.create_timeseries()

        # Then
        # Check that 1 `CoreTimeSeries` record is created per row of data
        assert CoreTimeSeries.objects.all().count() == len(example_timeseries_data)

        # Check the first `CoreTimeSeries` record was set
        # with the values from the first object in the original JSON
        core_timeseries_one = CoreTimeSeries.objects.first()
        self._assert_core_timeseries_model_has_correct_values(
            core_timeseries=core_timeseries_one,
            timeseries_data=example_timeseries_data[0],
        )

        # Check the second `CoreTimeSeries` record was set
        # with the correct corresponding the values as above
        core_timeseries_two = CoreTimeSeries.objects.last()
        self._assert_core_timeseries_model_has_correct_values(
            core_timeseries=core_timeseries_two,
            timeseries_data=example_timeseries_data[1],
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
        model: CoreHeadline | CoreTimeSeries, source_data: dict[str, str | float | int]
    ):
        assert model.metric.metric_group.topic.name == source_data["topic"]
        assert model.metric.metric_group.name == source_data["metric_group"]
        assert model.metric.name == source_data["metric"]
        assert model.geography.geography_type.name == source_data["geography_type"]
        assert model.geography.name == source_data["geography"]
        assert model.sex == {"all": "ALL", "female": "F", "male": "M"}.get(
            source_data["sex"].lower()
        )
        assert model.age.name == source_data["age"]
        assert model.stratum.name == source_data["stratum"]
        assert float(model.metric_value) == float(source_data["metric_value"])

    def _assert_core_headline_model_has_correct_values(
        self, core_headline: CoreHeadline, headline_data: dict[str, str | float]
    ) -> None:
        self._assert_core_model(model=core_headline, source_data=headline_data)

        assert str(core_headline.period_start) == headline_data["period_start"]
        assert str(core_headline.period_end) == headline_data["period_end"]
        assert str(core_headline.refresh_date) == headline_data["refresh_date"]

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
        timeseries_data: dict[str, str | float | int],
    ) -> None:
        self._assert_core_model(model=core_timeseries, source_data=timeseries_data)
        assert str(core_timeseries.refresh_date) == str(timeseries_data["refresh_date"])
        assert str(core_timeseries.date) == str(timeseries_data["date"])
        assert (
            core_timeseries.metric_frequency
            == TimePeriod[timeseries_data["metric_frequency"].title()].value
        )
        assert core_timeseries.year == timeseries_data["year"]
        assert core_timeseries.month == timeseries_data["month"]
        assert core_timeseries.epiweek == timeseries_data["epiweek"]
