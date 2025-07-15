import pytest

from metrics.data.models.core_models.supporting import Topic
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
