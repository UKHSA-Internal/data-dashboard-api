import datetime
from typing import Dict, Tuple, Union

import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers.plots import PlotSerializer
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.managers.metric_manager import FakeMetricManager
from tests.fakes.managers.topic_manager import FakeTopicManager

DATA_PAYLOAD_HINT = Dict[str, Union[str, datetime.date]]


@pytest.fixture
def plot_serializer_payload_and_model_managers() -> (
    Tuple[DATA_PAYLOAD_HINT, FakeMetricManager, FakeTopicManager]
):
    fake_metric = FakeMetricFactory.build_example_metric()
    fake_topic = fake_metric.topic

    data: DATA_PAYLOAD_HINT = {
        "topic": fake_topic.name,
        "metric": fake_metric.name,
    }

    return data, FakeMetricManager([fake_metric]), FakeTopicManager([fake_topic])


class TestPlotSerializer:
    optional_field_names = [
        "stratum",
        "geography",
        "geography_type",
    ]

    def test_validates_successfully_when_optional_parameters_are_none(
        self, plot_serializer_payload_and_model_managers
    ):
        """
        Given a valid payload containing None for every optional field
            passed to a `PlotSerializer` object
        And valid values for the `topic` and `metric`
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        optional_parameters_as_empty_strings = {
            field_name: None for field_name in self.optional_field_names
        }
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = plot_serializer_payload_and_model_managers
        valid_data_payload_with_optional_params = {
            **valid_data_payload,
            **optional_parameters_as_empty_strings,
        }

        serializer = PlotSerializer(
            data=valid_data_payload_with_optional_params,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    def test_validates_successfully_when_optional_parameters_are_empty_strings(
        self, plot_serializer_payload_and_model_managers
    ):
        """
        Given a valid payload containing empty strings for every optional field
            passed to a `PlotSerializer` object
        And valid values for the `topic` and `metric`
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        optional_parameters_as_empty_strings = {
            field_name: "" for field_name in self.optional_field_names
        }
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = plot_serializer_payload_and_model_managers
        valid_data_payload_with_optional_params = {
            **valid_data_payload,
            **optional_parameters_as_empty_strings,
        }

        serializer = PlotSerializer(
            data=valid_data_payload_with_optional_params,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    def test_validates_successfully_when_optional_parameters_not_provided(
        self, plot_serializer_payload_and_model_managers
    ):
        """
        Given a valid payload containing no optional fields
            passed to a `PlotSerializer` object
        And valid values for the `topic` and `metric`
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = plot_serializer_payload_and_model_managers

        for optional_param in self.optional_field_names:
            assert optional_param not in valid_data_payload

        serializer = PlotSerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    @pytest.mark.parametrize(
        "field_to_be_serialized",
        ["topic", "metric"],
    )
    def test_invalid_field_value(
        self,
        field_to_be_serialized: str,
        plot_serializer_payload_and_model_managers,
    ):
        """
        Given an invalid value passed to a field on the `PlotSerializer` object
        And valid values given to the remaining fields
        When `is_valid()` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        (
            data_payload,
            metric_manager,
            topic_manager,
        ) = plot_serializer_payload_and_model_managers
        data_payload[field_to_be_serialized] = "invalid-value"

        serializer = PlotSerializer(
            data=data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
