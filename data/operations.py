import io
from datetime import datetime
from typing import List

from apiv3.enums import TimePeriod
from apiv3.models import (
    Geography,
    GeographyType,
    Metric,
    Stratum,
    SubTheme,
    Theme,
    TimeSeries,
    Topic,
)


def _strip(text: str) -> str:
    return text.strip('"').strip("\n")


def _normalize_na_value(text: str) -> str:
    return "0" if "NA" in text else text


def _get_or_create_models(fields):
    theme, _ = Theme.objects.get_or_create(name=_strip(fields[0]))
    sub_theme, _ = SubTheme.objects.get_or_create(name=_strip(fields[1]), theme=theme)
    topic, _ = Topic.objects.get_or_create(
        name=_strip(fields[2]),
        sub_theme=sub_theme,
    )

    geography_type, _ = GeographyType.objects.get_or_create(name=_strip(fields[3]))
    geography, _ = Geography.objects.get_or_create(
        name=_strip(fields[4]),
        geography_type=geography_type,
    )

    metric, _ = Metric.objects.get_or_create(name=_strip(fields[5]), topic=topic)
    stratum, _ = Stratum.objects.get_or_create(name=_strip(fields[6]))

    metric_value = _normalize_na_value(text=fields[10])

    new_time_series = TimeSeries(
        epiweek=_strip(fields[8]),
        metric_value=metric_value,
        start_date=datetime.strptime(fields[9], "%Y-%m-%d"),
        year=_strip(fields[7]),
        period=TimePeriod.Weekly.value,
        metric=metric,
        stratum=stratum,
        geography=geography,
    )
    new_time_series.save()


def upload_data(data: io.TextIOWrapper) -> None:

    for index, line in enumerate(data, 0):

        fields: List[str] = line.split(",")
        if fields[0] != '"parent_theme"':
            try:
                _get_or_create_models(fields=fields)

            except ValueError:
                print(f"Error at line {index}")
