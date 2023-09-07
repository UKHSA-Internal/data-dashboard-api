import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers.tables import (
    TablePlotSerializer,
    TablesResponsePlotsListSerializer,
    TablesResponseSerializerV3,
    TablesResponseValueSerializer,
    TablesResponseValuesListSerializer,
    TablesSerializer,
)
from metrics.domain.models import PlotParameters, PlotsCollection


class TestTablePlotSerializer:
    optional_field_names = [
        "stratum",
        "geography",
        "geography_type",
        "sex",
        "label",
        "x_axis",
        "y_axis",
    ]

    def test_validates_successfully_when_optional_parameters_are_none(
        self, plot_serializer_payload_and_model_managers
    ):
        """
        Given a valid payload containing None for every optional field
            passed to a `TablePlotSerializer` object
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

        serializer = TablePlotSerializer(
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
            passed to a `TablePlotSerializer` object
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

        serializer = TablePlotSerializer(
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
            passed to a `TablePlotSerializer` object
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

        serializer = TablePlotSerializer(
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
            passed to a `TablePlotSerializer` object
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
        label = "15 to 44 years old"
        valid_data_payload["label"] = label

        serializer = TablePlotSerializer(
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

    @pytest.mark.parametrize("field_to_be_serialized", ["topic", "metric", "date_from"])
    def test_invalid_field_value(
        self,
        field_to_be_serialized: str,
        plot_serializer_payload_and_model_managers,
    ):
        """
        Given an invalid value passed to a field on the `TablePlotSerializer` object
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

        serializer = TablePlotSerializer(
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
        Given a valid payload passed to a `TablePlotSerializer` object
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
        serializer = TablePlotSerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # Then
        expected_metric_names: list[str] = metric_manager.get_all_names()
        assert list(serializer.fields["metric"].choices) == expected_metric_names

    def test_topic_manager_is_used_to_build_choices_for_field(
        self, plot_serializer_payload_and_model_managers
    ):
        """
        Given a valid payload passed to a `TablePlotSerializer` object
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
        serializer = TablePlotSerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
            },
        )

        # Then
        expected_topic_names: list[str] = topic_manager.get_all_names()
        assert list(serializer.fields["topic"].choices) == expected_topic_names


class TestTablesSerializer:
    def test_tables_serializer_validates_correctly(self):
        """
        Given the user supplies an empty plot to a `TablesSerializer` object
        When `is_valid()` is called from the serializer
        Then the serializer still validates successfully
        """
        # Given
        valid_data_payload = {
            "plots": [],
        }

        # When
        serializer = TablesSerializer(data=valid_data_payload)
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    def test_valid_payload_with_optional_x_and_y_fields_provided(
        self,
        plot_serializer_payload_and_model_managers,
    ):
        """
        Given a valid payload containing the optional `x_axis` & `y_axis` fields
            passed to a `TablesSerializer` object
        When `is_valid()` is called from the serializer
        Then the `x_axis` & `y_axis` field values are returned correctly
        """
        # Given
        x_axis = "date"
        y_axis = "metric"
        valid_data_payload = {"plots": [], "x_axis": x_axis, "y_axis": y_axis}

        serializer = TablesSerializer(
            data=valid_data_payload,
        )

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid
        assert serializer.validated_data["x_axis"] == x_axis
        assert serializer.validated_data["y_axis"] == y_axis

    def test_tables_serializer_does_not_validates(self):
        """
        Given the user supplies no payload to a `TablesSerializer` object
        When `is_valid()` is called from the serializer
        Then the serializer raises an exception
        """
        # Given
        serializer = TablesSerializer(data={})

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    @pytest.mark.parametrize("field_to_be_serialized", ["x_axis", "y_axis"])
    def test_invalid_field_value(
        self,
        field_to_be_serialized: str,
    ):
        """
        Given an invalid value passed to a field on the `TablesSerializer` object
        And valid values given to the remaining fields
        When `is_valid()` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        data_payload = {"plots": [], field_to_be_serialized: "invalid-value"}

        serializer = TablesSerializer(
            data=data_payload,
        )

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_to_models_returns_correct_models(self):
        """
        Given a payload for a list of 1 table plots
        When `to_models()` is called from an instance of the `TablesSerializer`
        Then a `TablePlots` model is returned with the correct data
        """
        # Given
        table_plots = [
            {
                "topic": "COVID-19",
                "metric": "COVID-19_deaths_ONSByDay",
                "stratum": "",
                "geography": "",
                "geography_type": "",
                "date_from": "",
                "chart_type": "",
            }
        ]
        valid_data_payload = {
            "file_format": "svg",
            "chart_height": 220,
            "chart_width": 515,
            "plots": table_plots,
            "x_axis": "date",
            "y_axis": "metric",
        }
        serializer = TablesSerializer(data=valid_data_payload)

        # When
        serializer.is_valid()
        table_plots_serialized_models: PlotsCollection = serializer.to_models()

        # Then
        table_plot_params_model = PlotParameters(**table_plots[0])
        expected_table_plots_model = PlotsCollection(
            plots=[table_plot_params_model],
            file_format=valid_data_payload["file_format"],
            chart_width=valid_data_payload["chart_width"],
            chart_height=valid_data_payload["chart_height"],
            x_axis=valid_data_payload["x_axis"],
            y_axis=valid_data_payload["y_axis"],
        )
        assert table_plots_serialized_models == expected_table_plots_model


class TestTablesResponseValueSerializer:
    def test_serializes_correctly(self):
        """
        Given a valid payload
        When the `TablesResponseValueSerializer` is serialized
        Then the validated data contains the serialized label and value
        """
        # Given
        label = "Label 1"
        value = "123"

        # When
        serializer = TablesResponseValueSerializer(
            data={"label": label, "value": value}
        )
        serializer.is_valid(raise_exception=True)

        # Then
        validated_data = serializer.validated_data
        assert validated_data["label"] == label
        assert validated_data["value"] == value


class TestTablesResponseValuesListSerializer:
    def test_serializes_correctly(self):
        """
        Given a valid payload
        When the `TablesResponseValuesListSerializer` is serialized
        Then the validated data contains
            the correct list serialized of label and value dicts
        """
        # Given
        valid_payload = [
            {"label": "Label 1", "value": "123"},
            {"label": "Label 2", "value": "456"},
        ]

        # When
        serializer = TablesResponseValuesListSerializer(data=valid_payload)
        serializer.is_valid(raise_exception=True)

        # Then
        validated_data = serializer.validated_data
        for validated_plot in validated_data:
            assert validated_plot in valid_payload


class TestTablesResponsePlotsListSerializer:
    def test_serializes_correctly(self):
        """
        Given a valid payload
        When the `TablesResponsePlotsListSerializer` is serialized
        Then the validated data contains the correct serialized data
        """
        # Given
        values_payload = [
            {"label": "Label 1", "value": "123"},
            {"label": "Label 2", "value": "456"},
        ]
        valid_payload = {
            "reference": "2023-01-01",
            "values": values_payload,
        }

        # When
        serializer = TablesResponsePlotsListSerializer(data=valid_payload)
        serializer.is_valid(raise_exception=True)

        # Then
        validated_data = serializer.validated_data
        assert validated_data["reference"] == valid_payload["reference"]
        assert validated_data["values"] == valid_payload["values"]


class TestTablesResponseSerializerV3:
    def test_serializes_correctly(self):
        """
        Given a valid payload
        When the `TablesResponseSerializerV3` is serialized
        Then the validated data contains the correct serialized data
        """
        # Given
        values_payload = [
            {"label": "Label 1", "value": "123"},
            {"label": "Label 2", "value": "456"},
        ]
        valid_payload = [
            {
                "reference": "2023-01-01",
                "values": values_payload,
            }
        ]

        # When
        serializer = TablesResponseSerializerV3(data=valid_payload)
        serializer.is_valid(raise_exception=True)

        # Then
        validated_plot = serializer.validated_data[0]
        assert validated_plot["reference"] == valid_payload[0]["reference"]
        assert validated_plot["values"] == valid_payload[0]["values"]
