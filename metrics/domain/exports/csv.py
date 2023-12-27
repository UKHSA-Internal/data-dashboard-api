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
    core_time_series_queryset,
) -> io.StringIO:
    writer = csv.writer(file)
    writer.writerow(FIELDS.keys())

    for core_time_series in core_time_series_queryset:
        writer.writerow(core_time_series)

    return file
