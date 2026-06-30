import pytest

from metrics.data.models.core_models.supporting import Metric, SubTheme, Theme, Topic
from tests.factories.metrics.topic import TopicFactory


class TestTopicManager:
    @pytest.mark.django_db
    def test_query_for_unique_names(self):
        """
        Given a number of existing `Topic` records
        When `get_all_unique_names` is called
        Then a unique set of `Topic` records is returned.
        """
        # Given
        fake_topic_name_one = "COVID-19"
        fake_topic_name_two = "Cold-alert"
        fake_topic_name_three = "COVID-19"

        TopicFactory(name=fake_topic_name_one)
        TopicFactory(name=fake_topic_name_two)
        TopicFactory(name=fake_topic_name_three)

        # When
        all_topic_names = Topic.objects.all()
        all_unique_topic_names = Topic.objects.get_all_unique_names()

        # Then
        assert all_topic_names.count() == 3
        assert all_unique_topic_names.count() == 2

    @pytest.mark.django_db
    def test_query_get_all_names_and_ids(self):
        """
        Given a number of existing `Topic` records
        When `get_all_names_and_ids` is called
        Then a unique set of `Topic` records is returned.
        """
        # Given
        fake_topic_name_one = "COVID-19"
        fake_topic_name_two = "Cold-alert"
        fake_topic_name_three = "Influenza"

        TopicFactory(name=fake_topic_name_one)
        TopicFactory(name=fake_topic_name_two)
        TopicFactory(name=fake_topic_name_three)

        # When
        get_all_names_and_ids = Topic.objects.get_all_names_and_ids()

        # Then
        assert get_all_names_and_ids.count() == 3

    @pytest.mark.django_db
    def test_query_get_name_by_id(self):
        """
        Given a number of existing `Topic` records
        When `get_name_by_id` is called
        Then a unique set of `Topic` records is returned.
        """
        # Given
        fake_topic_name_one = "COVID-19"
        fake_topic_name_two = "Cold-alert"
        fake_topic_name_three = "Influenza"

        TopicFactory(name=fake_topic_name_one)
        TopicFactory(name=fake_topic_name_two)
        TopicFactory(name=fake_topic_name_three)

        # When
        get_name_by_id = Topic.objects.get_name_by_id(3)

        # Then
        assert get_name_by_id == fake_topic_name_three

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "theme_name, sub_theme_name, topic_name, metric_name, is_match",
        [
            ("Infectious Diseases", "Respiratory", "COVID-19", "COVID-19_metric", True),
            ("NON-EXISTENT", "Respiratory", "COVID-19", "COVID-19_metric", False),
            (
                "Infectious Diseases",
                "NON-EXISTENT",
                "COVID-19",
                "COVID-19_metric",
                False,
            ),
            (
                "Infectious Diseases",
                "Respiratory",
                "NON-EXISTENT",
                "COVID-19_metric",
                False,
            ),
            ("Infectious Diseases", "Respiratory", "COVID-19", "NON-EXISTENT", False),
        ],
    )
    def test_get_id_by_name(
        self,
        theme_name: str,
        sub_theme_name: str,
        topic_name: str,
        metric_name: str,
        is_match: bool,
    ):
        """
        Given some theme, sub-theme, topic and metric records
        When get_theme_sub_theme_topic_and_metric_id_by_name() is called
        Then the matching 4 ids are returned, or 4 None values if the combination is not consistent
        """

        # Given
        given_theme = Theme.objects.create(name="Infectious Diseases")
        given_sub_theme = SubTheme.objects.create(name="Respiratory", theme=given_theme)
        given_topic = Topic.objects.create(name="COVID-19", sub_theme=given_sub_theme)
        given_metric = Metric.objects.create(name="COVID-19_metric", topic=given_topic)

        # When
        ids = Topic.objects.get_theme_sub_theme_topic_and_metric_id_by_name(
            theme_name, sub_theme_name, topic_name, metric_name
        )

        # Then
        expected_ids = (
            (
                given_theme.id,
                given_sub_theme.id,
                given_topic.id,
                given_metric.id,
            )
            if is_match
            else (None, None, None, None)
        )
        assert ids == expected_ids
