import datetime
from typing import Dict, List, Tuple, Union

import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers import ChartsQuerySerializer
from metrics.api.serializers.charts import ChartPlotSerializer
from metrics.domain.utils import ChartTypes
from tests.fakes.factories.metric_factory import FakeMetricFactory
from tests.fakes.managers.metric_manager import FakeMetricManager
from tests.fakes.managers.topic_manager import FakeTopicManager

DATA_PAYLOAD_HINT = Dict[str, Union[str, datetime.date]]


@pytest.fixture
def charts_plot_serializer_payload_and_model_managers() -> (
    Tuple[DATA_PAYLOAD_HINT, FakeMetricManager, FakeTopicManager]
):
    fake_metric = FakeMetricFactory.build_example_metric()
    fake_topic = fake_metric.topic

    data: DATA_PAYLOAD_HINT = {
        "topic": fake_topic.name,
        "metric": fake_metric.name,
        "chart_type": ChartTypes.line_with_shaded_section.value,
        "date_from": datetime.date(2023, 1, 1),
    }

    return data, FakeMetricManager([fake_metric]), FakeTopicManager([fake_topic])


class TestChartsQuerySerializer:
    @pytest.mark.parametrize("valid_file_format", ["svg", "png", "jpg", "jpeg"])
    def test_valid_file_format(self, valid_file_format: str):
        """
        Given a valid file format passed to a `ChartsQuerySerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        data = {"file_format": valid_file_format}
        serializer = ChartsQuerySerializer(data=data)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    def test_invalid_file_format(self):
        """
        Given an invalid file format passed to a `ChartsQuerySerializer` object
        When `is_valid(raise_exception=True)` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        data = {"file_format": "invalid.file.format"}
        serializer = ChartsQuerySerializer(data=data)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)


class TestChartPlotSerializer:
    @pytest.mark.parametrize("valid_chart_type", ChartTypes.choices())
    def test_valid_chart_type(
        self,
        valid_chart_type: Tuple[str, str],
        charts_plot_serializer_payload_and_model_managers,
    ):
        """
        Given a valid chart type passed to a `ChartPlotSerializer` object
        And valid values for the `topic` `metric` and `date_from`
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = charts_plot_serializer_payload_and_model_managers
        valid_data_payload["chart_type"] = valid_chart_type[0]

        serializer = ChartPlotSerializer(
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
        "field_to_be_serialized", ["topic", "metric", "chart_type", "date_from"]
    )
    def test_invalid_field_value(
        self,
        field_to_be_serialized: str,
        charts_plot_serializer_payload_and_model_managers,
    ):
        """
        Given an invalid value passed to a field on the `ChartPlotSerializer` object
        And valid values given to the remaining fields
        When `is_valid()` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        (
            data_payload,
            metric_manager,
            topic_manager,
        ) = charts_plot_serializer_payload_and_model_managers
        data_payload[field_to_be_serialized] = "invalid-value"

        serializer = ChartPlotSerializer(
            data=data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_metric_manager_is_used_to_build_choices_for_field(
        self, charts_plot_serializer_payload_and_model_managers
    ):
        """
        Given a valid payload passed to a `ChartPlotSerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `MetricManager` is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = charts_plot_serializer_payload_and_model_managers

        # When
        serializer = ChartPlotSerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # Then
        expected_metric_names: List[str] = metric_manager.get_all_names()
        assert list(serializer.fields["metric"].choices) == expected_metric_names

    def test_topic_manager_is_used_to_build_choices_for_field(
        self, charts_plot_serializer_payload_and_model_managers
    ):
        """
        Given a valid payload passed to a `ChartPlotSerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `TopicManager` is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = charts_plot_serializer_payload_and_model_managers

        # When
        serializer = ChartPlotSerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # Then
        expected_topic_names: List[str] = topic_manager.get_all_names()
        assert list(serializer.fields["topic"].choices) == expected_topic_names
