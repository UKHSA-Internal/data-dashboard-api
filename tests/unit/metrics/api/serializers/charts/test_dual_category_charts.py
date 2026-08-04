import copy

import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers.charts.dual_category_charts import (
    DualCategoryChartSegmentSerializer,
    DualCategoryChartSerializer,
)
from metrics.api.serializers.plots import PlotSerializer
from metrics.api.views.charts.dual_category_charts import (
    EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD,
)
from metrics.domain.charts import colour_scheme
from metrics.domain.common.utils import ChartAxisFields
from metrics.domain.models.charts.dual_category_charts import (
    DualCategoryChartRequestParams,
)
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.managers.metric_manager import FakeMetricManager
from tests.fakes.managers.topic_manager import FakeTopicManager

HEADLINE_METRIC = "COVID-19_headline_vaccines_spring24Uptake"
TIMESERIES_METRIC = "COVID-19_cases_rateRollingMean"


class TestDualCategoryChartSegmentSerializer:
    # Success cases
    def test_validates_successfully_with_all_required_fields(self):
        """
        Given a valid payload containing all required fields
            passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        valid_data_payload = {
            "secondary_field_value": "00-04",
            "colour": colour_scheme.RGBAChartLineColours.COLOUR_9_DEEP_PLUM.name,
            "label": "0 to 4 years",
        }

        serializer = DualCategoryChartSegmentSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    def test_validates_successfully_with_single_primary_field_value(self):
        """
        Given a valid payload containing a single primary field value
            passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        valid_data_payload = {
            "secondary_field_value": "00-04",
            "colour": colour_scheme.RGBAChartLineColours.COLOUR_10_PINK.name,
            "label": "0 to 4 years",
        }

        serializer = DualCategoryChartSegmentSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    @pytest.mark.parametrize(
        "valid_colour_choice", colour_scheme.RGBAChartLineColours.choices()
    )
    def test_validates_successfully_with_all_valid_colour_choices(
        self, valid_colour_choice: tuple[str, str]
    ):
        """
        Given a valid payload containing each valid colour choice
            passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        colour_value: str = valid_colour_choice[0]
        valid_data_payload = {
            "secondary_field_value": "00-04",
            "colour": colour_value,
            "label": "0 to 4 years",
        }

        serializer = DualCategoryChartSegmentSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid
        assert serializer.validated_data["colour"] == colour_value

    def test_validated_data_contains_correct_values(self):
        """
        Given a valid payload passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid()` is called from the serializer
        Then the validated_data contains the correct values
        """
        # Given
        primary_values = ["m", "f"]
        secondary_field_value = "00-04"
        colour = colour_scheme.RGBAChartLineColours.COLOUR_4_ORANGE.name
        label = "0 to 4 years"

        valid_data_payload = {
            "secondary_field_value": secondary_field_value,
            "colour": colour,
            "label": label,
        }

        serializer = DualCategoryChartSegmentSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid
        assert (
            serializer.validated_data["secondary_field_value"] == secondary_field_value
        )
        assert serializer.validated_data["colour"] == colour
        assert serializer.validated_data["label"] == label

    # Failure cases
    @pytest.mark.parametrize(
        "missing_field",
        [
            "secondary_field_value",
            "colour",
        ],
    )
    def test_invalid_when_required_field_is_missing(self, missing_field: str):
        """
        Given a payload missing a required field
            passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid(raise_exception=True)` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        complete_payload = {
            "secondary_field_value": "00-04",
            "colour": colour_scheme.RGBAChartLineColours.COLOUR_12_BLUE.name,
            "label": "0 to 4 years",
        }
        incomplete_payload = {
            k: v for k, v in complete_payload.items() if k != missing_field
        }

        serializer = DualCategoryChartSegmentSerializer(data=incomplete_payload)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_invalid_when_secondary_field_value_is_empty_string(self):
        """
        Given a payload where secondary_field_value is an empty string
            passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid(raise_exception=True)` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        invalid_data_payload = {
            "secondary_field_value": "",
            "colour": colour_scheme.RGBAChartLineColours.COLOUR_11_KHAKI.name,
            "label": "Test Label",
        }

        serializer = DualCategoryChartSegmentSerializer(data=invalid_data_payload)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_missing_label_is_still_deemed_valid(self):
        """
        Given a payload where label is an empty string
            passed to a `DualCategoryChartSegmentSerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        invalid_data_payload = {
            "secondary_field_value": "00-04",
            "colour": colour_scheme.RGBAChartLineColours.COLOUR_3_DARK_PINK.name,
            "label": "",
        }

        serializer = DualCategoryChartSegmentSerializer(data=invalid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid(raise_exception=True)

        # Then
        assert is_serializer_valid


class TestDualCategoryChartSerializer:
    # Success cases
    @pytest.mark.parametrize(
        "metric,x_axis,primary_field_values",
        [
            (HEADLINE_METRIC, "age", ["m", "f"]),
            (TIMESERIES_METRIC, "date", None),
            (TIMESERIES_METRIC, None, None),
        ],
    )
    def test_validation_with_valid_metric_and_primary_field_values_combination(
        self, metric: str, x_axis: str | None, primary_field_values: list[str] | None
    ):
        """
        Given a payload containing a valid metric and primary_field_values combination
            passed to a `DualCategoryChartSerializer` object
        When `validate()` is called from the serializer
        Then no ValidationError is raised and the data is returned unchanged
        """
        # Given
        valid_payload = EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD.copy()
        valid_payload["static_fields"] = valid_payload["static_fields"].copy()
        valid_payload["static_fields"]["metric"] = metric
        valid_payload["x_axis"] = x_axis
        valid_payload["primary_field_values"] = primary_field_values

        serializer = DualCategoryChartSerializer()

        # When
        is_valid = serializer.validate(attrs=valid_payload)

        # Then
        assert is_valid == valid_payload

    # Failure cases
    def test_validation_with_primary_field_values_for_timeseries_data(self):
        """
        Given a payload containing primary_field_values for a timeseries metric
            passed to a `DualCategoryChartSerializer` object
        When `validate()` is called from the serializer
        Then a `ValidationError` is raised as primary_field_values should not be provided
        """
        # Given
        invalid_payload = EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD.copy()
        invalid_payload["primary_field_values"] = ["m", "f"]

        serializer = DualCategoryChartSerializer()

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            serializer.validate(attrs=invalid_payload)

        assert exc_info.value.detail["primary_field_values"] == (
            "This field should not be provided for timeseries data."
        )

    def test_validation_with_non_date_x_axis_for_timeseries_data(self):
        """
        Given a payload containing a non-date x_axis for a timeseries metric
            passed to a `DualCategoryChartSerializer` object
        When `validate()` is called from the serializer
        Then a `ValidationError` is raised as x_axis must be date for timeseries data
        """
        # Given
        invalid_payload = EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD.copy()
        invalid_payload["x_axis"] = "age"

        serializer = DualCategoryChartSerializer()

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            serializer.validate(attrs=invalid_payload)

        assert exc_info.value.detail["x_axis"] == (
            "This field should be set to 'date' for timeseries data."
        )

    def test_validation_with_primary_field_values_missing_for_headline_data(self):
        """
        Given a payload containing a headline metric but no primary_field_values
            passed to a `DualCategoryChartSerializer` object
        When `validate()` is called from the serializer
        Then a `ValidationError` is raised as primary_field_values are required
        """
        # Given
        invalid_payload = EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD.copy()
        invalid_payload["static_fields"] = invalid_payload["static_fields"].copy()
        invalid_payload["static_fields"]["metric"] = HEADLINE_METRIC
        invalid_payload["x_axis"] = "age"
        invalid_payload.pop("primary_field_values", None)

        serializer = DualCategoryChartSerializer()

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            serializer.validate(attrs=invalid_payload)

        assert exc_info.value.detail["primary_field_values"] == (
            "This field is required for headline data."
        )

    def test_to_models_builds_timeseries_plots_when_x_axis_is_date(
        self, plot_serializer_payload_and_model_managers
    ):
        """
        Given a valid payload with x_axis set to date (timeseries)
        When `to_models()` is called from the serializer
        Then one plot per segment is returned without primary field values
        """
        # Given
        plot_payload, metric_manager, topic_manager = (
            plot_serializer_payload_and_model_managers
        )
        valid_payload = EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD.copy()
        valid_payload["x_axis"] = ChartAxisFields.date.name
        valid_payload.pop("primary_field_values", None)
        valid_payload["static_fields"]["topic"] = plot_payload["topic"]
        valid_payload["static_fields"]["metric"] = plot_payload["metric"]

        serializer_context = {
            "topic_manager": topic_manager,
            "metric_manager": metric_manager,
        }
        serializer = DualCategoryChartSerializer(
            data=valid_payload,
            context=serializer_context,
        )
        serializer.fields["static_fields"] = PlotSerializer(context=serializer_context)
        serializer.is_valid(raise_exception=True)

        # When
        result: DualCategoryChartRequestParams = serializer.to_models(request=None)

        # Then
        segments = valid_payload["segments"]
        secondary_category = valid_payload["secondary_category"]
        static_fields = valid_payload["static_fields"]

        assert result.primary_field_values == []
        assert len(result.plots) == len(segments)

        for index, segment in enumerate(segments):
            plot = result.plots[index]
            assert plot.x_axis == ChartAxisFields.date.name
            assert plot.y_axis == valid_payload["y_axis"]
            assert plot.line_colour == segment["colour"]
            assert plot.chart_type == valid_payload["chart_type"]
            assert getattr(plot, secondary_category) == segment["secondary_field_value"]
            assert plot.topic == static_fields["topic"]
            assert plot.metric == static_fields["metric"]
            assert plot.date_from == static_fields["date_from"]
            assert plot.date_to == static_fields["date_to"]

    def test_to_models_builds_headline_plots_with_primary_field_values(self):
        """
        Given a valid payload with a headline metric and primary field values
        When `to_models()` is called from the serializer
        Then one plot per segment is returned for each primary field value
        """
        # Given
        fake_metric = FakeMetricFactory.build_example_metric(
            metric_name=HEADLINE_METRIC,
            metric_group_name="headline",
        )
        fake_topic = fake_metric.metric_group.topic
        metric_manager = FakeMetricManager([fake_metric])
        topic_manager = FakeTopicManager([fake_topic])
        valid_payload = EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD.copy()
        valid_payload["static_fields"] = valid_payload["static_fields"].copy()
        valid_payload["static_fields"]["topic"] = fake_topic.name
        valid_payload["static_fields"]["metric"] = HEADLINE_METRIC
        valid_payload["x_axis"] = ChartAxisFields.sex.name
        valid_payload["primary_field_values"] = ["m", "f"]

        serializer_context = {
            "topic_manager": topic_manager,
            "metric_manager": metric_manager,
        }
        serializer = DualCategoryChartSerializer(
            data=valid_payload,
            context=serializer_context,
        )
        serializer.fields["static_fields"] = PlotSerializer(context=serializer_context)
        serializer.is_valid(raise_exception=True)

        # When
        result: DualCategoryChartRequestParams = serializer.to_models(request=None)

        # Then
        segments = valid_payload["segments"]
        secondary_category = valid_payload["secondary_category"]
        x_axis = valid_payload["x_axis"]

        assert result.primary_field_values == ["m", "f"]
        assert len(result.plots) == len(segments) * len(
            valid_payload["primary_field_values"]
        )

        for index, plot in enumerate(result.plots):
            segment_index = index % len(segments)
            primary_index = index // len(segments)
            segment = segments[segment_index]
            primary_field_value = valid_payload["primary_field_values"][primary_index]

            assert plot.x_axis == x_axis
            assert getattr(plot, x_axis) == primary_field_value
            assert getattr(plot, secondary_category) == segment["secondary_field_value"]
            assert plot.line_colour == segment["colour"]
