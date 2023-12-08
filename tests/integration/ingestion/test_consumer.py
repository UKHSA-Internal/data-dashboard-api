import pytest

from ingestion.utils.type_hints import INCOMING_DATA_TYPE
from ingestion.v2.consumer import ConsumerV2
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

EXPECTED_EMBARGO_FORMAT = "%Y-%m-%d %H:%M:%S"


class TestConsumerV2:
    @pytest.mark.django_db
    def test_can_ingest_headline_data_successfully(
        self, example_headline_data_v2: INCOMING_DATA_TYPE
    ):
        """
        Given an example headline data file
        When `create_core_headlines()` is called
            from an instance of `Consumer`
        Then `CoreHeadline` records are created with the correct values
        """
        # Given
        consumer = ConsumerV2(source_data=example_headline_data_v2)
        assert CoreHeadline.objects.all().count() == 0

        # When
        consumer.create_core_headlines()

        # Then
        # Check that 1 `CoreHeadline` record is created per row of data
        assert CoreHeadline.objects.all().count() == len(
            example_headline_data_v2["data"]
        )

        # Check the first `CoreHeadline` record was set
        # with the values from the first object in the original JSON
        core_headline_one = CoreHeadline.objects.first()
        self._assert_core_headline_model_has_correct_values(
            core_headline=CoreHeadline.objects.first(),
            main_headline_data=example_headline_data_v2,
            headline_specific_data=example_headline_data_v2["data"][0],
        )

        # Check the second `CoreHeadline` record was set
        # with the correct corresponding the values as above
        core_headline_two = CoreHeadline.objects.last()
        self._assert_core_headline_model_has_correct_values(
            core_headline=CoreHeadline.objects.last(),
            main_headline_data=example_headline_data_v2,
            headline_specific_data=example_headline_data_v2["data"][1],
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
        self, example_time_series_data_v2: INCOMING_DATA_TYPE
    ):
        """
        Given an example headline data file
        When `create_core_time_series()` is called
            from an instance of `Consumer`
        Then `CoreTimeSeries` records are created with the correct values
        """
        # Given
        consumer = ConsumerV2(source_data=example_time_series_data_v2)
        assert CoreTimeSeries.objects.all().count() == 0

        # When
        consumer.create_core_time_series()

        # Then
        # Check that 1 `CoreTimeSeries` record is created per row of data
        assert CoreTimeSeries.objects.all().count() == len(
            example_time_series_data_v2["time_series"]
        )

        # Check the first `CoreTimeSeries` record was set
        # with the values from the first object in the original JSON
        core_timeseries_one = CoreTimeSeries.objects.first()
        self._assert_core_timeseries_model_has_correct_values(
            core_timeseries=core_timeseries_one,
            main_timeseries_data=example_time_series_data_v2,
            timeseries_specific_data=example_time_series_data_v2["time_series"][0],
        )

        # Check the second `CoreTimeSeries` record was set
        # with the correct corresponding the values as above
        core_timeseries_two = CoreTimeSeries.objects.last()
        self._assert_core_timeseries_model_has_correct_values(
            core_timeseries=core_timeseries_two,
            main_timeseries_data=example_time_series_data_v2,
            timeseries_specific_data=example_time_series_data_v2["time_series"][1],
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
        assert str(model.refresh_date) == source_data["refresh_date"]

    def _assert_core_headline_model_has_correct_values(
        self,
        core_headline: CoreHeadline,
        main_headline_data: INCOMING_DATA_TYPE,
        headline_specific_data: dict[str, str | float],
    ) -> None:
        self._assert_core_model(model=core_headline, source_data=main_headline_data)

        assert str(core_headline.period_start) == headline_specific_data["period_start"]
        assert str(core_headline.period_end) == headline_specific_data["period_end"]
        assert (
            str(core_headline.metric_value)
            == f"{headline_specific_data['metric_value']:.4f}"
        )
        assert (
            core_headline.embargo.strftime(EXPECTED_EMBARGO_FORMAT)
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
