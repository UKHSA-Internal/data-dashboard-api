from typing import Dict, List, Tuple

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError

from metrics.api.serializers.charts import ChartsResponseSerializer
from metrics.api.serializers.stats import HeadlinesResponseSerializer
from metrics.api.serializers.trends import TrendsQuerySerializer, TrendsResponseSerializer
from tests.fakes.factories.metric_factory import FakeMetricFactory
from tests.fakes.managers.metric_manager import FakeMetricManager
from tests.fakes.managers.topic_manager import FakeTopicManager


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


class TestTrendsResponseSerializer:
    def test_can_validate_successfully(self):
        """
        Given a valid payload containing the correct associated trends fields
        When `is_valid()` is called from an instance of the `TrendsResponseSerializer`
        Then True is returned
        """
        # Given
        payload = {
            "metric_name": "new_cases_7days_change",
            "metric_value": 10,
            "percentage_metric_name": "new_cases_7days_change_percentage",
            "percentage_metric_value": 3.2,
            "direction": "up",
            "colour": "red",
        }

        serializer = TrendsResponseSerializer(data=payload)

        # When
        validated: bool = serializer.is_valid()

        # Then
        assert validated


class TestChartsResponseSerializer:
    def test_can_validate_successfully(self):
        """
        Given a valid payload containing an image file
        When `is_valid()` is called from an instance of the `ChartsResponseSerializer`
        Then True is returned
        """
        # Given
        chart = SimpleUploadedFile(
            name="test_image.jpg",
            content_type="image/png",
            content=b"chart_image",
        )

        payload = {
            "chart": chart,
        }

        serializer = ChartsResponseSerializer(data=payload)

        # When
        validated: bool = serializer.is_valid()

        # Then
        assert validated


class TestHeadlinesResponseSerializer:
    def test_can_validate_successfully(self):
        """
        Given a valid payload containing the correct associated headline value field
        When `is_valid()` is called from an instance of the `HeadlinesResponseSerializer`
        Then True is returned
        """
        # Given
        payload = {
            "value": 10,
        }

        serializer = HeadlinesResponseSerializer(data=payload)

        # When
        validated: bool = serializer.is_valid()

        # Then
        assert validated
