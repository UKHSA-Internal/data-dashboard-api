import pytest

from metrics.domain.utils import ChartAxisFields, get_axis_name


class TestGetAxisName:
    test_values = [(enums.value, enums.name) for enums in ChartAxisFields]
    test_values.append(("not_a_field", "not_a_field"))

    @pytest.mark.parametrize("field_name, expected_result", test_values)
    def test_get_axis_field_name(self, field_name: str, expected_result: str):
        """
        Given a field name (eg. stratum__name)
        When `get_axis_field_name()` is called
        Then the expected output will be returned
        """

        # Given
        input_field_name: str = field_name

        # When
        actual_result: str = get_axis_name(field_name=input_field_name)

        # Then
        assert actual_result == expected_result

    @pytest.mark.parametrize(
        "valid_name",
        [
            "stratum",
            "date",
            "metric",
            "geography",
        ],
    )
    def test_get_x_axis_value_for_valid_name(self, valid_name: str):
        """
        Given a name of an axis type
        When `get_x_axis_value()` is called from the `ChartAxisFields` enum class
        Then the correct value is returned
        """
        # Given
        valid_axis_name = valid_name

        # When
        axis_value = ChartAxisFields.get_x_axis_value(name=valid_axis_name)

        # Then
        assert axis_value == ChartAxisFields[valid_axis_name].value

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "",
            "-",
            None,
        ],
    )
    def test_get_x_axis_value_for_invalid_name_returns_default(self, invalid_name: str):
        """
        Given an invalid name for an axis type
        When `get_x_axis_value()` is called from the `ChartAxisFields` enum class
        Then the value of the default of `date` is returned
        """
        # Given
        invalid_axis_name = invalid_name

        # When
        axis_value = ChartAxisFields.get_x_axis_value(name=invalid_axis_name)

        # Then
        assert axis_value == ChartAxisFields.date.value

    @pytest.mark.parametrize(
        "valid_name",
        [
            "stratum",
            "date",
            "metric",
            "geography",
        ],
    )
    def test_get_y_axis_value_for_valid_name(self, valid_name: str):
        """
        Given a name of an axis type
        When `get_y_axis_value()` is called from the `ChartAxisFields` enum class
        Then the correct value is returned
        """
        # Given
        valid_axis_name = valid_name

        # When
        axis_value = ChartAxisFields.get_y_axis_value(name=valid_axis_name)

        # Then
        assert axis_value == ChartAxisFields[valid_axis_name].value

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "",
            "-",
            None,
        ],
    )
    def test_get_y_axis_value_for_invalid_name_returns_default(self, invalid_name: str):
        """
        Given an invalid name for an axis type
        When `get_y_axis_value()` is called from the `ChartAxisFields` enum class
        Then the value of the default of `metric` is returned
        """
        # Given
        invalid_axis_name = invalid_name

        # When
        axis_value = ChartAxisFields.get_y_axis_value(name=invalid_axis_name)

        # Then
        assert axis_value == ChartAxisFields.metric.value
