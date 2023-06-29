from typing import List, Tuple

import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers.charts import (
    ChartPlotSerializer,
    ChartsSerializer,
    EncodedChartResponseSerializer,
    EncodedChartsRequestSerializer,
)
from metrics.domain.charts import colour_scheme
from metrics.domain.charts.line_multi_coloured import properties
from metrics.domain.models import PlotParameters, PlotsCollection
from metrics.domain.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_X_AXIS,
    DEFAULT_Y_AXIS,
    ChartTypes,
)


class TestChartPlotSerializer:
    optional_field_names = [
        "stratum",
        "geography",
        "geography_type",
        "sex",
        "label",
        "line_colour",
        "line_type",
        "x_axis",
        "y_axis",
    ]

    def test_validates_successfully_when_optional_parameters_are_none(
        self, plot_serializer_payload_and_model_managers
    ):
        """
        Given a valid payload containing None for every optional field
            passed to a `ChartPlotSerializer` object
        And valid values for the `topic` `metric` and `chart_type`
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        optional_parameters_as_none = {
            field_name: None for field_name in self.optional_field_names
        }
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = plot_serializer_payload_and_model_managers
        valid_data_payload_with_optional_params = {
            **valid_data_payload,
            **optional_parameters_as_none,
        }

        serializer = ChartPlotSerializer(
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
            passed to a `ChartPlotSerializer` object
        And valid values for the `topic` `metric` and `chart_type`
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

        serializer = ChartPlotSerializer(
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
            passed to a `ChartPlotSerializer` object
        And valid values for the `topic` `metric` and `chart_type`
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

    def test_valid_payload_with_optional_label_field_provided(
        self,
        plot_serializer_payload_and_model_managers,
    ):
        """
        Given a valid payload containing the optional `label` field
            passed to a `ChartPlotSerializer` object
        And valid values for the `topic` `metric` and `chart_type`
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = plot_serializer_payload_and_model_managers
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

    @pytest.mark.parametrize(
        "valid_colour_choice", colour_scheme.RGBAChartLineColours.choices()
    )
    def test_valid_payload_with_optional_line_colour_field_provided(
        self,
        valid_colour_choice: Tuple[str, str],
        plot_serializer_payload_and_model_managers,
    ):
        """
        Given a valid payload containing the optional `line_colour` field
            passed to a `ChartPlotSerializer` object
        And valid values for the `topic` `metric` and `chart_type`
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = plot_serializer_payload_and_model_managers
        line_colour: str = valid_colour_choice[0]
        valid_data_payload["line_colour"] = line_colour

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
        assert serializer.validated_data["line_colour"] == line_colour

    @pytest.mark.parametrize(
        "valid_line_type_choice", properties.ChartLineTypes.choices()
    )
    def test_valid_payload_with_optional_line_type_field_provided(
        self,
        valid_line_type_choice: Tuple[str, str],
        plot_serializer_payload_and_model_managers,
    ):
        """
        Given a valid payload containing the optional `line_type` field
            passed to a `ChartPlotSerializer` object
        And valid values for the `topic` `metric` and `chart_type`
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = plot_serializer_payload_and_model_managers
        line_type: str = valid_line_type_choice[0]
        valid_data_payload["line_type"] = line_type

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
        assert serializer.validated_data["line_type"] == line_type

    @pytest.mark.parametrize("valid_chart_type", ChartTypes.choices())
    def test_valid_chart_type(
        self,
        valid_chart_type: Tuple[str, str],
        plot_serializer_payload_and_model_managers,
    ):
        """
        Given a valid chart type passed to a `ChartPlotSerializer` object
        And valid values for the `topic` `metric` and `chart_type`
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = plot_serializer_payload_and_model_managers
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
        "field_to_be_serialized",
        ["topic", "metric", "chart_type", "date_from"],
    )
    def test_invalid_field_value(
        self,
        field_to_be_serialized: str,
        plot_serializer_payload_and_model_managers,
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
        ) = plot_serializer_payload_and_model_managers
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
        self, plot_serializer_payload_and_model_managers
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
        ) = plot_serializer_payload_and_model_managers

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
        self, plot_serializer_payload_and_model_managers
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
        ) = plot_serializer_payload_and_model_managers

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

    def test_to_models_returns_chart_plot_parameters_model(
        self,
        plot_serializer_payload_and_model_managers,
    ):
        """
        Given a valid payload passed to a `ChartPlotSerializer` object
        When `to_models()` is called from the serializer
        Then a `ChartPlotParameters` model is returned with the correct fields
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
        ) = plot_serializer_payload_and_model_managers
        valid_data_payload["stratum"] = "0_4"
        valid_data_payload["geography"] = "England"
        valid_data_payload["geography_type"] = "Nation"

        serializer = ChartPlotSerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # When
        serializer.is_valid(raise_exception=True)
        chart_plot_parameters: PlotParameters = serializer.to_models()

        # Then
        assert chart_plot_parameters.topic == valid_data_payload["topic"]
        assert chart_plot_parameters.metric == valid_data_payload["metric"]
        assert chart_plot_parameters.stratum == valid_data_payload["stratum"]
        assert chart_plot_parameters.geography == valid_data_payload["geography"]
        assert (
            chart_plot_parameters.geography_type == valid_data_payload["geography_type"]
        )


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

    def test_chart_width_and_height_are_returned_correctly(self):
        """
        Given the user supplies chart width and height parameters to pass to a `ChartsSerializer` object
        When `is_valid()` is called from the serializer
        Then the supplied values are used
        """
        # Given
        fake_chart_width = 100
        fake_chart_height = 200
        valid_data_payload = {
            "file_format": "svg",
            "plots": [],
            "chart_width": fake_chart_width,
            "chart_height": fake_chart_height,
        }

        serializer = ChartsSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()
        serializer_data = serializer.data

        # Then
        assert is_serializer_valid
        assert serializer_data["chart_width"] == fake_chart_width
        assert serializer_data["chart_height"] == fake_chart_height

    def test_width_and_height_are_not_supplied(self):
        """
        Given the user does not supply a width and/or height parameter
          to pass to a `ChartsSerializer` object
        When `is_valid()` is called from the serializer
        Then the default values for them are used
        """
        # Given
        valid_data_payload = {
            "file_format": "svg",
            "plots": [],
        }

        serializer = ChartsSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()
        serializer_data = serializer.data

        # Then
        assert is_serializer_valid
        assert serializer_data["chart_width"] == DEFAULT_CHART_WIDTH
        assert serializer_data["chart_height"] == DEFAULT_CHART_HEIGHT

    @pytest.mark.parametrize("chart_parameter", ["chart_width", "chart_height"])
    def test_width_or_height_are_invalid_format(self, chart_parameter: str):
        """
        Given the user supplies an invalid width and/or height parameter
          to pass to a `ChartsSerializer` object
        When `is_valid()` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        bad_data_payload = {
            "file_format": "svg",
            "plots": [],
            chart_parameter: "bad_value",
        }

        serializer = ChartsSerializer(data=bad_data_payload)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_width_and_height_are_none_into_model(self):
        """
        Given the user supplies a None value for the width and/or height parameter
          to pass to a `ChartsSerializer` object
        When `to_models()` is called from an instance of the `ChartsSerializer`
        Then the default values for them are used
        """
        # Given
        valid_data_payload = {
            "file_format": "svg",
            "chart_width": None,
            "chart_height": None,
            "plots": [],
        }

        serializer = ChartsSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()
        serialized_model_data: PlotsCollection = serializer.to_models()

        # Then
        assert is_serializer_valid
        assert serialized_model_data.chart_width == DEFAULT_CHART_WIDTH
        assert serialized_model_data.chart_height == DEFAULT_CHART_HEIGHT

    def test_x_and_y_axis_are_none_into_model(
        self, plot_serializer_payload_and_model_managers
    ):
        """
        Given the user supplies a None value for the x_axis and/or y_axis parameter
          to pass to a `ChartsSerializer` object
        When `to_models()` is called from an instance of the `ChartsSerializer`
        Then the default values for them are used
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
        valid_data_payload = {
            "file_format": "svg",
            "chart_height": 300,
            "chart_width": 400,
            "plots": chart_plots,
            "x_axis": None,
            "y_axis": None,
        }
        serializer = ChartsSerializer(data=valid_data_payload)

        # When
        serializer.is_valid()
        serialized_model_data: PlotsCollection = serializer.to_models()

        # Then
        assert serialized_model_data.plots[0].x_axis == DEFAULT_X_AXIS
        assert serialized_model_data.plots[0].y_axis == DEFAULT_Y_AXIS

    def test_to_models_returns_correct_models(self):
        """
        Given a payload for a list of 1 chart plot
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
        valid_data_payload = {
            "file_format": "svg",
            "chart_height": 300,
            "chart_width": 400,
            "plots": chart_plots,
        }
        serializer = ChartsSerializer(data=valid_data_payload)

        # When
        serializer.is_valid()
        chart_plots_serialized_models: PlotsCollection = serializer.to_models()

        # Then
        chart_plot_params_model = PlotParameters(**chart_plots[0])
        expected_chart_plots_model = PlotsCollection(
            plots=[chart_plot_params_model],
            file_format=valid_data_payload["file_format"],
            chart_height=valid_data_payload["chart_height"],
            chart_width=valid_data_payload["chart_width"],
            x_axis=DEFAULT_X_AXIS,
            y_axis=DEFAULT_Y_AXIS,
        )
        assert chart_plots_serialized_models == expected_chart_plots_model

    def test_valid_payload_with_optional_x_and_y_fields_provided(self):
        """
        Given a valid payload containing the optional `x_axis` & `y_axis` fields
            passed to a `ChartsSerializer` object
        When `is_valid()` is called from the serializer
        Then the `x_axis` & `y_axis` field values are returned correctly
        """
        # Given
        x_axis = "stratum"
        y_axis = "metric"
        chart_plots = [
            {
                "topic": "COVID-19",
                "metric": "cases_rate_age_sex",
                "stratum": "",
                "geography": "",
                "geography_type": "",
                "date_from": "",
                "chart_type": "bar",
            }
        ]
        valid_data_payload = {
            "file_format": "svg",
            "chart_height": 300,
            "chart_width": 400,
            "plots": chart_plots,
            "x_axis": x_axis,
            "y_axis": y_axis,
        }
        serializer = ChartsSerializer(data=valid_data_payload)

        # When
        serializer.is_valid()
        serialized_model_data: PlotsCollection = serializer.to_models()

        # Then
        assert serialized_model_data.plots[0].x_axis == x_axis
        assert serialized_model_data.plots[0].y_axis == y_axis


class TestEncodedChartsRequestSerializer:
    def test_valid_file_format(
        self,
    ):
        """
        Given a valid file format of `svg` passed
            to an `EncodedChartsRequestSerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        valid_data_payload = {"file_format": "svg", "plots": []}
        serializer = EncodedChartsRequestSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    @pytest.mark.parametrize("invalid_file_format", ["png", "jpg", "jpeg"])
    def test_invalid_file_format(self, invalid_file_format: str):
        """
        Given an invalid file format passed
            to an `EncodedChartsRequestSerializer` object
        When `is_valid(raise_exception=True)` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        invalid_data_payload = {
            "file_format": invalid_file_format,
            "plots": [],
        }
        serializer = EncodedChartsRequestSerializer(data=invalid_data_payload)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)


class TestEncodedChartResponseSerializer:
    def test_has_payload(self):
        """
        Given a valid payload passed to a `EncodedChartResponseSerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        valid_data_payload = {"last_updated": "has_value", "chart": "has_value"}
        serializer = EncodedChartResponseSerializer(data=valid_data_payload)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    def test_invalid_payload(self):
        """
        Given an invalid payload passed to a `EncodedChartResponseSerializer` object
        When `is_valid(raise_exception=True)` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        invalid_data_payload = {"last_updated": None, "chart": None}

        serializer = EncodedChartResponseSerializer(data=invalid_data_payload)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
