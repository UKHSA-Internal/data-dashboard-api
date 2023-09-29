import io

from metrics.domain.exports.csv import write_data_to_csv
from tests.fakes.factories.metrics.api_time_series_factory import (
    FakeAPITimeSeriesFactory,
)
from tests.fakes.models.metrics.api_time_series import FakeAPITimeSeries


def _get_line_from_stream(filestream: io.StringIO) -> list[str]:
    return filestream.readline().strip().split(",")


class TestWriteDataToCSV:
    expected_csv_header = [
        "theme",
        "sub_theme",
        "topic",
        "geography_type",
        "geography",
        "metric",
        "sex",
        "age",
        "stratum",
        "year",
        "date",
        "metric_value",
    ]

    def test_for_basic_behaviour(self):
        """
        Given a file and a QuerySet
        When `write_data_to_csv()` is called
        Then the expected output will be returned
        """
        # Given
        regular_api_time_series: FakeAPITimeSeries = (
            FakeAPITimeSeriesFactory.build_example_covid_time_series()
        )

        # When
        file = io.StringIO()
        csv_file: io.StringIO = write_data_to_csv(
            file=file, api_time_series=[regular_api_time_series]
        )
        # Go back to the beginning of stream
        csv_file.seek(0)

        # Output should consiste of two rows, a heading and the data itself
        csv_header = _get_line_from_stream(csv_file)
        csv_body = _get_line_from_stream(csv_file)

        # Then
        expected_csv_body = [
            "infectious_disease",
            "respiratory",
            "COVID-19",
            "Nation",
            "England",
            "COVID-19_deaths_ONSByDay",
            "all",
            "75+",
            "default",
            "2023",
            "2023-03-08",
            "2364",
        ]
        assert csv_header == self.expected_csv_header
        assert csv_body == expected_csv_body

    def test_fields_missing(self):
        """
        Given a file and a QuerySet with some expected fields missing. eg geography_type,
        When `write_data_to_csv()` is called
        Then the expected output will be returned
        """

        # Given
        api_time_series_additional: FakeAPITimeSeries = (
            FakeAPITimeSeriesFactory.build_example_api_time_series_fields_missing()
        )
        # When
        file = io.StringIO()
        csv_file: io.StringIO = write_data_to_csv(
            file=file, api_time_series=[api_time_series_additional]
        )
        # Go back to the beginning of stream
        csv_file.seek(0)

        # Output should consist of two rows, a heading and the data itself
        csv_header = _get_line_from_stream(csv_file)
        csv_body = _get_line_from_stream(csv_file)

        # Then
        expected_csv_body = [
            "infectious_disease",
            "respiratory",
            "COVID-19",
            "",  # geography type
            "",  # geography
            "COVID-19_deaths_ONSByDay",
            "",  # sex
            "",  # age
            "default",  # stratum
            "",  # year
            "2023-03-08",
            "2364",
        ]

        assert csv_header == self.expected_csv_header
        assert csv_body == expected_csv_body
