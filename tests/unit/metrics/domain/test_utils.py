import pytest

from metrics.domain.utils import ChartAxisFields, get_axis_name


class TestGetAxisName:
    test_values = [(enums.value, enums.name) for enums in ChartAxisFields]
    test_values.append(("not_a_field", "not_a_field"))

    @pytest.mark.parametrize("field_name, expected_result", test_values)
    def test_get_axis_field_name(self, field_name: str, expected_result: str):
        """Given a field name (eg. stratum__name)
        When `get_axis_field_name()` is called
        Then the expected output will be returned
        """

        # Given
        input_field_name: str = field_name

        # When
        actual_result: str = get_axis_name(field_name=input_field_name)

        # Then
        assert actual_result == expected_result
