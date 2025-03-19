import datetime
import io
from unittest import mock

from metrics.domain.exports.csv_output import FIELDS, write_data_to_csv
from metrics.api.serializers.timeseries import CoreTimeSeriesSerializer
from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)
from tests.unit.metrics.api.serializers.test_timeseries import mock_core_times_series


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
        "in_reporting_delay_period",
    ]

    def test_for_basic_behaviour(self, mock_core_times_series: mock.MagicMock):
        """
        Given a file and a QuerySet
        When `write_data_to_csv()` is called
        Then the expected output will be returned
        """
        # Given
        expected_date = datetime.datetime(year=2024, month=1, day=1)
        expected_metric_value = 1.0000
        expected_topic = "COVID-19"
        expected_metric = "COVID-19_cases_rateRollingMean"
        expected_age = "all"
        expected_sex = "all"
        expected_in_reporting_delay_period = True

        fake_core_time_series = FakeCoreTimeSeriesFactory.build_time_series(
            date=expected_date,
            metric_name=expected_metric,
            topic_name=expected_topic,
            age_name=expected_age,
            sex=expected_sex,
            metric_value=expected_metric_value,
            in_reporting_delay_period=expected_in_reporting_delay_period,
        )
        mocked_core_time_series = mock_core_times_series
        serializer = CoreTimeSeriesSerializer(
            instance=[mocked_core_time_series], many=True
        )
        data = serializer.data

        # When
        file = io.StringIO()
        csv_file: io.StringIO = write_data_to_csv(
            file=file,
            serialized_core_time_series=data,
        )
        # Go back to the beginning of stream
        csv_file.seek(0)

        # Output should consiste of two rows, a heading and the data itself
        csv_header = _get_line_from_stream(csv_file)
        csv_body = _get_line_from_stream(csv_file)

        # Then
        expected_csv_body = [
            fake_core_time_series.metric.topic.sub_theme.theme.name,
            fake_core_time_series.metric.topic.sub_theme.name,
            expected_topic,
            fake_core_time_series.geography.geography_type.name,
            fake_core_time_series.geography.name,
            expected_metric,
            expected_sex,
            expected_age,
            fake_core_time_series.stratum.name,
            str(fake_core_time_series.year),
            expected_date.strftime("%Y-%m-%d"),
            f"{expected_metric_value:.4f}",
            str(expected_in_reporting_delay_period),
        ]
        assert csv_header == self.expected_csv_header
        assert csv_body == expected_csv_body
