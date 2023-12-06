import pytest

from ingestion.utils import type_hints
from ingestion.utils.enums import DataSourceFileType
from ingestion.v2.consumer import Consumer


class TestConsumerProperties:
    def test_is_headline_data_returns_true_for_headline_metric_group(
        self, example_headline_data: type_hints.INCOMING_DATA_TYPE
    ):
        """
        Given input data with a `metric_group` value of "headline"
        When `is_headline_data` is called
            from an instance of the `Consumer`
        Then True is returned
        """
        # Given
        fake_data = example_headline_data
        consumer = Consumer(source_data=fake_data)

        # When
        is_headline_data: bool = consumer.is_headline_data

        # Then
        assert is_headline_data

    @pytest.mark.parametrize(
        "metric_group",
        [
            DataSourceFileType.cases.value,
            DataSourceFileType.deaths.value,
            DataSourceFileType.healthcare.value,
            DataSourceFileType.testing.value,
            DataSourceFileType.vaccinations.value,
        ],
    )
    def test_is_headline_data_returns_false_for_other_metric_groups(
        self,
        metric_group: str,
        example_time_series_data: type_hints.INCOMING_DATA_TYPE,
    ):
        """
        Given input data with a `metric_group` value other than "headline"
        When `is_headline_data` is called
            from an instance of the `Consumer`
        Then False is returned
        """
        # Given
        fake_data = example_time_series_data
        fake_data["metric_group"] = metric_group
        consumer = Consumer(source_data=fake_data)

        # When
        is_headline_data: bool = consumer.is_headline_data

        # Then
        assert not is_headline_data
