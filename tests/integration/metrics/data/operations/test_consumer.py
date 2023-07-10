import json

import pytest

from ingestion.consumer import Ingestion
from metrics.data.models.core_models import CoreHeadline


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
    def _assert_core_headline_models_share_same_supporting_models(
        core_headline_one: CoreHeadline, core_headline_two: CoreHeadline
    ) -> None:
        assert core_headline_one.metric == core_headline_two.metric
        assert (
            core_headline_one.metric.metric_group
            == core_headline_two.metric.metric_group
        )
        assert (
            core_headline_one.metric.metric_group.topic
            == core_headline_two.metric.metric_group.topic
        )
        assert (
            core_headline_one.metric.metric_group.topic.sub_theme
            == core_headline_two.metric.metric_group.topic.sub_theme
        )
        assert (
            core_headline_one.metric.metric_group.topic.sub_theme.theme
            == core_headline_two.metric.metric_group.topic.sub_theme.theme
        )
        assert core_headline_one.age == core_headline_two.age

    @pytest.mark.django_db
    def test_can_ingest_data_successfully(
        self, example_headline_data_json: list[dict[str, float]]
    ):
        """
        Given an example headline data file
        When `create_headlines()` is called
            from an instance of `Ingestion`
        Then a `Headline` record is created with the correct values
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
        self._assert_core_headline_models_share_same_supporting_models(
            core_headline_one=core_headline_one,
            core_headline_two=core_headline_two,
        )
