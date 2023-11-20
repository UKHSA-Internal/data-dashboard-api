import pytest

from ingestion.file_ingestion import DataSourceFileType
from ingestion.v2.consumer import ConsumerV2


class TestConsumerProperties:
    def test_is_headline_data_returns_true_for_headline_metric_group(self):
        """
        Given input data with a `metric_group` value of "headline"
        When `is_headline_data` is called
            from an instance of the `Consumer`
        Then True is returned
        """
        # Given
        fake_data = {"metric_group": DataSourceFileType.headline.value}
        consumer = ConsumerV2(data=fake_data)

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
        self, metric_group: str
    ):
        """
        Given input data with a `metric_group` value other than "headline"
        When `is_headline_data` is called
            from an instance of the `Consumer`
        Then False is returned
        """
        # Given
        fake_data = {"metric_group": metric_group}
        consumer = ConsumerV2(data=fake_data)

        # When
        is_headline_data: bool = consumer.is_headline_data

        # Then
        assert not is_headline_data
