from typing import List

from django.db.models import Manager, QuerySet

from apiv3.api_models import WeeklyTimeSeries

DEFAULT_WEEKLY_TIME_SERIES_MANAGER = WeeklyTimeSeries.objects


def get_weekly_disease_incidence(
    topic: str,
    metric: str,
    year: int = 2022,
    weekly_time_series_manager: Manager = DEFAULT_WEEKLY_TIME_SERIES_MANAGER,
) -> List[int]:

    ordered_time_series_for_topic: QuerySet = weekly_time_series_manager.filter(
        topic=topic,
        metric=metric,
        year=year,
    ).order_by("start_date")

    flattened_metric_values: QuerySet = ordered_time_series_for_topic.values_list(
        "metric_value", flat=True
    )

    return list(flattened_metric_values)


if __name__ == "__main__":
    incidences = get_weekly_disease_incidence(topic="Influenza", metric="weekly_positivity")

    print(incidences)
