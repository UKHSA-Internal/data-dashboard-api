import csv
import io
from collections.abc import Iterable
from typing import Any

FIELDS = {
    "theme": "metric__topic__sub_theme__theme__name",
    "sub_theme": "metric__topic__sub_theme__name",
    "topic": "metric__topic__name",
    "geography_type": "geography__geography_type__name",
    "geography": "geography__name",
    "metric": "metric__name",
    "sex": "sex",
    "age": "age__name",
    "stratum": "stratum__name",
    "year": "year",
    "date": "date",
    "metric_value": "metric_value",
    "in_reporting_delay_period": "in_reporting_delay_period",
    "is_public": "is_public",
}

HEADLINE_FIELDS = {
    "theme": "metric__topic__sub_theme__theme__name",
    "sub_theme": "metric__topic__sub_theme__name",
    "topic": "metric__topic__name",
    "geography_type": "geography__geography_type__name",
    "geography": "geography__name",
    "metric": "metric__name",
    "sex": "sex",
    "age": "age__name",
    "stratum": "stratum__name",
    "period_start": "period_start",
    "period_end": "period_end",
    "metric_value": "metric_value",
    "is_public": "is_public",
}


def write_data_to_csv(
    *,
    file: io.StringIO,
    serialized_core_time_series: dict[str, Any],
) -> io.StringIO:
    headers = [field for field in FIELDS if field != "is_public"]
    rows = [
        [record[field] for field in headers] for record in serialized_core_time_series
    ]
    return _write_to_csv_file(file=file, headers=headers, rows=rows)


def _write_to_csv_file(
    *, file: io.StringIO, headers: list[str], rows: Iterable
) -> io.StringIO:
    writer = csv.writer(file)
    writer.writerow(headers)

    for row in rows:
        writer.writerow(row)

    return file


def write_headline_data_to_csv(
    *,
    file: io.StringIO,
    core_headline_data: Iterable,
) -> io.StringIO:
    headers = list(HEADLINE_FIELDS.keys())
    rows = core_headline_data
    return _write_headline_to_csv_file(file=file, headers=headers, rows=rows)


def _write_headline_to_csv_file(
    *, file: io.StringIO, headers: list[str], rows: Iterable
) -> io.StringIO:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)

    return file
