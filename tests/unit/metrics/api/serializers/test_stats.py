from typing import Dict, List, Tuple

import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers.stats import (
    HeadlinesQuerySerializer,
    TrendsQuerySerializer,
)
from tests.fakes.factories.metric_factory import FakeMetricFactory
from tests.fakes.managers.metric_manager import FakeMetricManager
from tests.fakes.managers.topic_manager import FakeTopicManager


class TestHeadlinesQuerySerializer:
    DATA_PAYLOAD_HINT = Dict[str, str]

    @classmethod
    def _setup_valid_data_payload_and_model_managers(
        cls,
    ) -> Tuple[DATA_PAYLOAD_HINT, FakeMetricManager, FakeTopicManager]:
        fake_metric = FakeMetricFactory.build_example_metric(
            metric_name="new_cases_7days_sum"
        )
        fake_topic = fake_metric.topic

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
        Then the result of `get_all_names()` from the `MetricManager` is used to populate the correct field choices
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
        expected_metric_names: List[str] = metric_manager.get_all_names()
        assert list(serializer.fields["metric"].choices) == expected_metric_names

    def test_topic_manager_is_used_to_build_choices_for_field(self):
        """
        Given a valid payload passed to a `ChartsRequestSerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `TopicManager` is used to populate the correct field choices
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
        expected_topic_names: List[str] = topic_manager.get_all_names()
        assert list(serializer.fields["topic"].choices) == expected_topic_names


class TestTrendsQuerySerializer:
    DATA_PAYLOAD_HINT = Dict[str, str]

    @classmethod
    def _setup_valid_data_payload_and_model_managers(
        cls,
    ) -> Tuple[DATA_PAYLOAD_HINT, FakeMetricManager, FakeTopicManager]:
        base_metric_name = "new_tests_7days_change"

        fake_metric = FakeMetricFactory.build_example_metric(
            metric_name=base_metric_name
        )
        fake_topic = fake_metric.topic
        fake_percentage_metric = FakeMetricFactory.build_example_metric(
            metric_name=f"{base_metric_name}_percentage"
        )

        data: cls.DATA_PAYLOAD_HINT = {
            "topic": fake_topic.name,
            "metric": fake_metric.name,
            "percentage_metric": fake_percentage_metric.name,
        }

        return (
            data,
            FakeMetricManager([fake_metric, fake_percentage_metric]),
            FakeTopicManager([fake_topic]),
        )

    def test_can_validate_successfully(self):
        """
        Given a valid payload passed to the `TrendsQuerySerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        (
            data_payload,
            metric_manager,
            topic_manager,
        ) = self._setup_valid_data_payload_and_model_managers()

        serializer = TrendsQuerySerializer(
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

    @pytest.mark.parametrize(
        "field_to_be_serialized", ["topic", "metric", "percentage_metric"]
    )
    def test_invalid_field_value(self, field_to_be_serialized: str):
        """
        Given an invalid value passed to a field on the `TrendsQuerySerializer` object
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

        serializer = TrendsQuerySerializer(
            data=data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_metric_manager_is_used_to_build_choices_for_metric_field(self):
        """
        Given a valid payload passed to a `TrendsQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_unique_change_type_names()` from the `MetricManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = self._setup_valid_data_payload_and_model_managers()

        # When
        serializer = TrendsQuerySerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # Then
        expected_metric_names: List[
            str
        ] = metric_manager.get_all_unique_change_type_names()
        assert list(serializer.fields["metric"].choices) == expected_metric_names

    def test_metric_manager_is_used_to_build_choices_for_percentage_metric_field(self):
        """
        Given a valid payload passed to a `TrendsQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_unique_percent_change_type_names()` from the `MetricManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = self._setup_valid_data_payload_and_model_managers()

        # When
        serializer = TrendsQuerySerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # Then
        expected_metric_names: List[
            str
        ] = metric_manager.get_all_unique_percent_change_type_names()
        assert (
            list(serializer.fields["percentage_metric"].choices)
            == expected_metric_names
        )

    def test_topic_manager_is_used_to_build_choices_for_field(self):
        """
        Given a valid payload passed to a `TrendsQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `TopicManager` is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = self._setup_valid_data_payload_and_model_managers()

        # When
        serializer = TrendsQuerySerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # Then
        expected_topic_names: List[str] = topic_manager.get_all_names()
        assert list(serializer.fields["topic"].choices) == expected_topic_names
