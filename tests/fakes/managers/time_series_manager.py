import datetime
from typing import Any, Iterable

from django.db import models

from metrics.data.managers.core_models.time_series import CoreTimeSeriesManager
from tests.fakes.models.metrics.rbac_models.rbac_permission import FakeRBACPermission
from tests.fakes.models.queryset import FakeQuerySet
from tests.fakes.models.row import FakeRow


class FakeCoreTimeSeriesManager(CoreTimeSeriesManager):
    """
    A fake version of the `CoreTimeSeriesManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, time_series, **kwargs):
        self.time_series = time_series
        super().__init__(**kwargs)

    def get_count(
        self,
        x_axis: str,
        y_axis: str,
        topic_name: str,
        metric_name: str,
        date_from: datetime.datetime | str,
        date_to: datetime.datetime | str,
    ) -> int:
        date_from = _convert_string_to_date(date_string=date_from)

        filtered_for_metric_topic_and_date = [
            x
            for x in self.time_series
            if x.metric.metric_group.topic.name == topic_name
            if x.metric.name == metric_name
            if x.date >= date_from
            if x.date <= date_to
        ]
        return len(filtered_for_metric_topic_and_date)

    def query_for_data(
        self,
        topic_name: str,
        metric_name: str,
        date_from: datetime.date,
        fields_to_export: list[str] | None = None,
        date_to: datetime.date | None = None,
        field_to_order_by: str = "date",
        geography_name: str | None = None,
        geography_type_name: str | None = None,
        stratum_name: str | None = None,
        sex: str | None = None,
        age: str | None = None,
        rbac_permissions: Iterable[FakeRBACPermission] | None = None,
    ) -> FakeQuerySet:
        date_from = _convert_string_to_date(date_string=date_from)

        filtered_time_series = [
            time_series
            for time_series in self.time_series
            if time_series.metric.metric_group.topic.name == topic_name
            if time_series.metric.name == metric_name
            if time_series.date > date_from
            if time_series.date < date_to
        ]

        if geography_name:
            filtered_time_series = [
                x for x in filtered_time_series if x.geography.name == geography_name
            ]

        if geography_type_name:
            filtered_time_series = [
                x
                for x in filtered_time_series
                if x.geography.geography_type.name == geography_name
            ]

        if stratum_name:
            filtered_time_series = [
                x for x in filtered_time_series if x.stratum.name == stratum_name
            ]

        if sex:
            filtered_time_series = [x for x in filtered_time_series if x.sex == sex]

        if age:
            filtered_time_series = [x for x in filtered_time_series if x.age == age]

        if fields_to_export:
            queryset = FakeQuerySet(
                [
                    self._export_record(
                        time_series=time_series, fields_to_export=fields_to_export
                    )
                    for time_series in filtered_time_series
                ]
            )
        else:
            queryset = FakeQuerySet(filtered_time_series)

        queryset.latest_date = max(
            (x.refresh_date for x in filtered_time_series), default=""
        )
        return queryset

    @classmethod
    def _export_record(cls, time_series, fields_to_export) -> dict[str, Any]:
        exported_record = {}
        for field in fields_to_export:
            exported_record[field] = getattr(time_series, field)
        return exported_record

    def exists(self) -> bool:
        return bool(self.time_series)

    def get_available_geographies(self, topic: str) -> models.QuerySet:
        rows = [
            FakeRow(
                geography__name=obj.geography.name,
                geography__geography_type__name=obj.geography.geography_type.name,
            )
            for obj in self.time_series
            if obj.metric.topic.name == topic
        ]
        return FakeQuerySet(instances=rows)


def _convert_string_to_date(date_string: str | datetime.datetime) -> datetime.date:
    """Convenience function to convert date strings to `datetime.date` objects.

    Notes:
        The Django ORM supports dates as strings or as `datetime.date` objects.
        This function is used to mimic that behavior.

    Args:
        date_string (str): The date string to convert.

    Returns:
        `datetime.date: The converted date as an object.

    """
    if isinstance(date_string, str):
        return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()

    if isinstance(date_string, datetime.datetime):
        return date_string.date()

    return date_string
