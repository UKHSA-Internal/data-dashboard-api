from typing import Any, TypeAlias
import datetime
from collections import defaultdict
from decimal import Decimal

from metrics.api.packages.permissions import (
    FluentPermissions,
    FluentPermissionsError,
)
from metrics.data.models.rbac_models import (
    RBACPermission,
)
from metrics.domain.common.utils import ChartAxisFields

PlotData: TypeAlias = dict[str, list[datetime.date | Decimal | bool | str]]


def filter_queryset(cls, value, info) -> PlotData:
    context = info.context
    request = context["request"]
    fields_to_export = context["fields_to_export"]
    plot_parameters = context["plot_parameters"]
    plot_data = _get_fields_to_export(fields_to_export=fields_to_export)

    for data in value:
        if data.get("is_public", None) is True:
            if _is_age_chart(plot_parameters=plot_parameters):
                data = _aggregate_results_by_age(data=data)
            plot_data = _aggregate_results(plot_data=plot_data, data=data)
            continue

        data = _get_rbac_field_values(data=data)

        group_permissions: list[RBACPermission] = getattr(
            request, "group_permissions", []
        )

        f = FluentPermissions(
            data=data,
            group_permissions=group_permissions,
        ) \
            .add_field("theme") \
            .add_field("sub_theme") \
            .add_field("topic") \
            .add_field("geography_type") \
            .add_field("geography") \
            .add_field("metric") \
            .add_field("age") \
            .add_field("stratum") \
            .execute()
        try:
            f.validate()
            if _is_age_chart(plot_parameters=plot_parameters):
                data = _aggregate_results_by_age(data=data)
            plot_data = _aggregate_results(plot_data=plot_data, data=data)
        except FluentPermissionsError:
            pass
    return plot_data


def _is_age_chart(*, plot_parameters) -> bool:
    return plot_parameters.x_axis == ChartAxisFields.age.name


def _aggregate_results(*, plot_data: PlotData, data: Any) -> PlotData:
    for field in plot_data.keys():
        plot_data[field].append(data[field])
    return plot_data


def _aggregate_results_by_age(*, data: Any) -> dict[str, Any]:
    # {'age__name': ['00 - 04'], 'metric_value': [Decimal('1.3000')]}
    age: str = data[ChartAxisFields.age.value]
    data[ChartAxisFields.age.value] = _build_age_display_name(value=age)
    return data


def _build_age_display_name(*, value: str) -> str:
    return value.replace("-", " - ")


def _get_fields_to_export(*, fields_to_export: list[str]) -> dict[str, list[str]]:
    return {field: [] for field in fields_to_export}


def _get_rbac_field_values(*, data: Any) -> dict[str, str]:
    try:
        return {
            "theme": data["theme"],
            "sub_theme": data["sub_theme"],
            "topic": data["topic"],
            "geography_type": data["geography_type"],
            "geography": data["geography"],
            "metric": data["metric"],
            "age": data["age"],
            "stratum": data["stratum"],
        }
    except AttributeError:
        return {}
