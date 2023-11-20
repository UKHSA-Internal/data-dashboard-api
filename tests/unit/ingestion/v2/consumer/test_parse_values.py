import pytest

from ingestion.v2.consumer import ConsumerV2
from metrics.data.enums import TimePeriod


class TestConsumerParseValueMethods:
    @pytest.mark.parametrize(
        "sex_attribute_value, expected_value",
        (
            ["all", "all"],
            ["female", "f"],
            ["male", "m"],
        ),
    )
    def test_parse_sex_value(self, sex_attribute_value: str, expected_value: str):
        """
        Given a "sex" value in the provided "data"
        When `_parse_sex_value()` is called
            from an instance of the `Consumer`
        Then the correct string is returned
        """
        # Given
        fake_data = {"sex": sex_attribute_value}
        consumer = ConsumerV2(data=fake_data)

        # When
        parsed_sex_value: str = consumer._parse_sex_value()

        # Then
        assert parsed_sex_value == expected_value

    @pytest.mark.parametrize(
        "metric_frequency_attribute_value, expected_value",
        (
            ["daily", TimePeriod.Daily.value],
            ["weekly", TimePeriod.Weekly.value],
            ["monthly", TimePeriod.Monthly.value],
            ["quarterly", TimePeriod.Quarterly.value],
            ["annual", TimePeriod.Annual.value],
        ),
    )
    def test_parse_metric_frequency_value(
        self, metric_frequency_attribute_value: str, expected_value: str
    ):
        """
        Given a "metric_frequency" value in the provided "data"
        When `_parse_metric_frequency_value()` is called
            from an instance of the `Consumer`
        Then the correct string is returned
        """
        # Given
        fake_data = {"metric_frequency": metric_frequency_attribute_value}
        consumer = ConsumerV2(data=fake_data)

        # When
        parsed_metric_frequency: str = consumer._parse_metric_frequency_value()

        # Then
        assert parsed_metric_frequency == expected_value
