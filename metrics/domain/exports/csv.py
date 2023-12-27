import csv
import io

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
    "epiweek": "epiweek",
    "date": "date",
    "metric_value": "metric_value",
}


def write_data_to_csv(
    file: io.StringIO,
    api_time_series: list[APITimeSeries],
) -> io.StringIO:
    writer = csv.writer(file)
    writer.writerow(COLUMNS_TO_WRITE)

    for time_series in api_time_series:
        time_series_attributes = [getattr(time_series, key) for key in COLUMNS_TO_WRITE]
        writer.writerow(time_series_attributes)

    return file
