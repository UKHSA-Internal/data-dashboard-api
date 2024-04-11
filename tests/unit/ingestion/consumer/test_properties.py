import pytest

from ingestion.consumer import Consumer
from ingestion.utils import type_hints
from ingestion.utils.enums import DataSourceFileType


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
        "metric, metric_group",
        (
            ("COVID-19_deaths_ONSByDay", DataSourceFileType.deaths.value),
            ("COVID-19_cases_casesByDay", DataSourceFileType.cases.value),
            ("RSV_healthcare_admissionRateByWeek", DataSourceFileType.healthcare.value),
            ("hMPV_testing_positivityByWeek", DataSourceFileType.testing.value),
            (
                "COVID-19_vaccinations_autumn22_dosesByDay",
                DataSourceFileType.vaccinations.value,
            ),
        ),
    )
    def test_is_headline_data_returns_false_for_other_metric_groups(
        self,
        metric: str,
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
        fake_data["metric"] = metric
        consumer = Consumer(source_data=fake_data)

        # When
        is_headline_data: bool = consumer.is_headline_data

        # Then
        assert not is_headline_data
