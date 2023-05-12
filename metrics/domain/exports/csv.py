import csv
import io
from typing import List

from metrics.data.models.api_models import APITimeSeries

COLUMNS_TO_WRITE = [
    "theme",
    "sub_theme",
    "topic",
    "geography_type",
    "geography",
    "metric",
    "stratum",
    "sex",
    "year",
    "dt",
    "metric_value",
]


def write_data_to_csv(
    file: io.StringIO,
    api_time_series: List[APITimeSeries],
) -> io.StringIO:
    writer = csv.writer(file)
    writer.writerow(COLUMNS_TO_WRITE)

    for time_series in api_time_series:
        time_series_attributes = [getattr(time_series, key) for key in COLUMNS_TO_WRITE]
        writer.writerow(time_series_attributes)

    return file
