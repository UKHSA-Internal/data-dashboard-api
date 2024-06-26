from unittest import mock

import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers.headlines import (
    HeadlinesQuerySerializer,
)
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.managers.age_manager import FakeAgeManager
from tests.fakes.managers.geography_manager import FakeGeographyManager
from tests.fakes.managers.geography_type_manager import FakeGeographyTypeManager
from tests.fakes.managers.metric_manager import FakeMetricManager
from tests.fakes.managers.stratum_manager import FakeStratumManager
from tests.fakes.managers.topic_manager import FakeTopicManager


class TestHeadlinesQuerySerializer:
    DATA_PAYLOAD_HINT = dict[str, str]

    @classmethod
    def _setup_valid_data_payload_and_model_managers(
        cls,
    ) -> tuple[DATA_PAYLOAD_HINT, FakeMetricManager, FakeTopicManager]:
        fake_metric = FakeMetricFactory.build_example_metric(
            metric_name="COVID-19_headline_ONSdeaths_7DayTotals",
            metric_group_name="headline",
        )
        fake_topic = fake_metric.metric_group.topic

        data: cls.DATA_PAYLOAD_HINT = {
            "topic": fake_topic.name,
            "metric": fake_metric.name,
        }

        return data, FakeMetricManager([fake_metric]), FakeTopicManager([fake_topic])

    def test_can_validate_successfully(self):
        """
        Given a valid payload passed to the `HeadlinesQuerySerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        (
            data_payload,
            metric_manager,
            topic_manager,
        ) = self._setup_valid_data_payload_and_model_managers()

        serializer = HeadlinesQuerySerializer(
            data=data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # When
        validated: bool = serializer.is_valid()

        # Then
        assert validated

    @pytest.mark.parametrize("field_to_be_serialized", ["topic", "metric"])
    def test_invalid_field_value(self, field_to_be_serialized: str):
        """
        Given an invalid value passed to a field on the `HeadlinesQuerySerializer` object
        And valid values given to the remaining fields
        When `is_valid()` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        (
            data_payload,
            metric_manager,
            topic_manager,
        ) = self._setup_valid_data_payload_and_model_managers()
        data_payload[field_to_be_serialized] = "invalid-value"

        serializer = HeadlinesQuerySerializer(
            data=data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_metric_manager_is_used_to_build_choices_for_field(self):
        """
        Given a valid payload passed to a `HeadlinesQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `MetricManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = self._setup_valid_data_payload_and_model_managers()

        # When
        serializer = HeadlinesQuerySerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # Then
        expected_metric_names: list[str] = metric_manager.get_all_headline_names()
        assert list(serializer.fields["metric"].choices) == expected_metric_names

    def test_topic_manager_is_used_to_build_choices_for_field(self):
        """
        Given a valid payload passed to a `HeadlinesQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `TopicManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = self._setup_valid_data_payload_and_model_managers()

        # When
        serializer = HeadlinesQuerySerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # Then
        expected_topic_names: list[str] = topic_manager.get_all_names()
        assert list(serializer.fields["topic"].choices) == expected_topic_names

    def test_geography_manager_is_used_to_build_choices_for_field(self):
        """
        Given a valid payload passed to a `HeadlinesQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `GeographyManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = self._setup_valid_data_payload_and_model_managers()
        geography_manager = FakeGeographyManager(geographies=[mock.Mock()])

        # When
        serializer = HeadlinesQuerySerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
                "geography_manager": geography_manager,
                "geography_type_manager": FakeGeographyTypeManager([]),
                "stratum_manager": FakeStratumManager([]),
                "age_manager": FakeAgeManager([]),
            },
        )

        # Then
        expected_geography_names: list[str] = geography_manager.get_all_names()
        assert list(serializer.fields["geography"].choices) == expected_geography_names

    def test_geography_type_manager_is_used_to_build_choices_for_field(self):
        """
        Given a valid payload passed to a `HeadlinesQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `GeographyTypeManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = self._setup_valid_data_payload_and_model_managers()
        geography_type_manager = FakeGeographyTypeManager(geography_types=[mock.Mock()])

        # When
        serializer = HeadlinesQuerySerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
                "geography_type_manager": geography_type_manager,
                "geography_manager": FakeGeographyManager([]),
                "stratum_manager": FakeStratumManager([]),
                "age_manager": FakeAgeManager([]),
            },
        )

        # Then
        expected_geography_type_names: list[str] = (
            geography_type_manager.get_all_names()
        )
        assert (
            list(serializer.fields["geography_type"].choices)
            == expected_geography_type_names
        )

    def test_stratum_manager_is_used_to_build_choices_for_field(self):
        """
        Given a valid payload passed to a `HeadlinesQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `StratumManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = self._setup_valid_data_payload_and_model_managers()
        stratum_manager = FakeStratumManager(strata=[mock.Mock()])

        # When
        serializer = HeadlinesQuerySerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
                "stratum_manager": stratum_manager,
                "geography_manager": FakeGeographyManager([]),
                "geography_type_manager": FakeGeographyTypeManager([]),
                "age_manager": FakeAgeManager([]),
            },
        )

        # Then
        expected_stratum_names: list[str] = stratum_manager.get_all_names()
        assert list(serializer.fields["stratum"].choices) == expected_stratum_names

    def test_age_manager_is_used_to_build_choices_for_field(self):
        """
        Given a valid payload passed to a `HeadlinesQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `AgeManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = self._setup_valid_data_payload_and_model_managers()
        age_manager = FakeAgeManager(ages=[mock.Mock()])

        # When
        serializer = HeadlinesQuerySerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
                "age_manager": age_manager,
                "geography_manager": FakeGeographyManager([]),
                "geography_type_manager": FakeGeographyTypeManager([]),
                "stratum_manager": FakeStratumManager([]),
            },
        )

        # Then
        expected_age_names: list[str] = age_manager.get_all_names()
        assert list(serializer.fields["age"].choices) == expected_age_names
