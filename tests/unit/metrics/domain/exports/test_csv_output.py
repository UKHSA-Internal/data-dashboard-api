import datetime
import io

from metrics.domain.exports.csv_output import FIELDS, write_data_to_csv
from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)
from tests.fakes.models.metrics.core_time_series import FakeCoreTimeSeries
from tests.fakes.models.queryset import FakeQuerySet


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

    def test_for_basic_behaviour(self):
        """
        Given a file and a QuerySet
        When `write_data_to_csv()` is called
        Then the expected output will be returned
        """
        # Given
        expected_date = datetime.datetime(year=2023, month=3, day=8)
        expected_metric_value = 2364
        expected_topic = "COVID-19"
        expected_metric = "COVID-19_deaths_ONSByDay"
        expected_age = "75+"
        expected_sex = "all"
        expected_in_reporting_delay_period = False

        fake_core_time_series: FakeCoreTimeSeries = (
            FakeCoreTimeSeriesFactory.build_time_series(
                date=datetime.datetime(year=2023, month=3, day=8),
                metric_value=expected_metric_value,
                topic=expected_topic,
                metric=expected_metric,
                age_name=expected_age,
                sex=expected_sex,
                in_reporting_delay_period=expected_in_reporting_delay_period,
            )
        )
        queryset = FakeQuerySet(instances=[fake_core_time_series]).values_list(
            *FIELDS.values()
        )

        # When
        file = io.StringIO()
        csv_file: io.StringIO = write_data_to_csv(
            file=file,
            core_time_series_queryset=queryset,
            headers=None,
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
            str(expected_date),
            str(expected_metric_value),
            str(expected_in_reporting_delay_period),
        ]
        assert csv_header == self.expected_csv_header
        assert csv_body == expected_csv_body
