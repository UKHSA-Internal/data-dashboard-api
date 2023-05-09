import datetime
from typing import Dict, List, Tuple, Union

import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers import ChartsQuerySerializer
from metrics.api.serializers.charts import ChartPlotSerializer, ChartsSerializer
from metrics.domain.models import ChartPlotParameters, ChartPlots
from metrics.domain.utils import ChartTypes
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
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
        "date_to": datetime.date(2023, 5, 1),
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
    def test_valid_payload_with_optional_fields_provided(
        self,
        charts_plot_serializer_payload_and_model_managers,
    ):
        """
        Given a valid payload containing the optional `label` field passed to a `ChartPlotSerializer` object
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
        label = "15 to 44 years old"
        valid_data_payload["label"] = label

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
        assert serializer.validated_data["label"] == label

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


class TestChartsSerializer:
    @pytest.mark.parametrize("valid_file_format", ["svg", "png", "jpg", "jpeg"])
    def test_valid_file_format(
        self,
        valid_file_format: str,
    ):
        """
        Given a valid file format passed to a `ChartsSerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        valid_data_payload = {"file_format": valid_file_format, "plots": []}

        serializer = ChartsSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    def test_invalid_file_format(self):
        """
        Given an invalid file format passed to a `ChartsSerializer` object
        When `is_valid(raise_exception=True)` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        invalid_data_payload = {
            "file_format": "invalid.file.format",
            "plots": [],
        }

        serializer = ChartsSerializer(data=invalid_data_payload)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_to_models_returns_correct_models(self):
        """
        Given a payload for a list of 1 chart plots
        When `to_models()` is called from an instance of the `ChartsSerializer`
        Then a `ChartPlots` model is returned with the correct data
        """
        # Given
        chart_plots = [
            {
                "topic": "COVID-19",
                "metric": "new_cases_daily",
                "stratum": "",
                "geography": "",
                "geography_type": "",
                "date_from": "",
                "chart_type": "line_with_shaded_section",
            }
        ]
        valid_data_payload = {"file_format": "svg", "plots": chart_plots}
        serializer = ChartsSerializer(data=valid_data_payload)

        # When
        serializer.is_valid()
        chart_plots_serialized_models: ChartPlots = serializer.to_models()

        # Then
        chart_plot_params_model = ChartPlotParameters(**chart_plots[0])
        expected_chart_plots_model = ChartPlots(
            plots=[chart_plot_params_model],
            file_format=valid_data_payload["file_format"],
        )
        assert chart_plots_serialized_models == expected_chart_plots_model
