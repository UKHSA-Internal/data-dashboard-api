from typing import TypedDict

from django.apps import apps

WILDCARD_ID_VALUE = "-1"

"""
    A few classes with type hints to represent our complete 
    JWT permission set hierarchy. Please do import and use 
    this from other modules too to keep us safe & well.
"""
class PermissionRowType(TypedDict):
    theme: dict[str, str]
    sub_theme: dict[str, str]
    topic: dict[str, str]
    metric: dict[str, str]
    geography_type: dict[str, str]
    geography: dict[str, str]


class PermissionSetSummaryType(TypedDict):
    has_global_access: bool


class PermissionSetsType(TypedDict):
    permission_sets: list[PermissionRowType]
    summary: PermissionSetSummaryType


def check_permissions_by_name(
    *,
    permission_sets: PermissionSetsType,
    theme_name: str,
    sub_theme_name: str,
    topic_name: str,
    metric_name: str,
    geography_type: str,
    geography_name: str,
) -> bool:
    """
    Convert permission resource names into ids before evaluating chart permissions.
    """

    if not isinstance(permission_sets, dict):
        return False
    if not isinstance(permission_sets.get("permission_sets"), list):
        return False
    if not isinstance(permission_sets.get("summary"), dict):
        return False
    if not isinstance(permission_sets.get("summary").get("has_global_access"), bool):
        return False

    if permission_sets.get("summary").get("has_global_access"):
        return True

    topic_model = apps.get_model("data", "Topic")
    metric_model = apps.get_model("data", "Metric")
    geography_type_model = apps.get_model("data", "GeographyType")
    geography_model = apps.get_model("data", "Geography")

    topic_manager = getattr(topic_model, "objects")
    metric_manager = getattr(metric_model, "objects")
    geography_type_manager = getattr(geography_type_model, "objects")
    geography_manager = getattr(geography_model, "objects")

    theme_id, sub_theme_id, topic_id = topic_manager.get_id_by_name(
        theme_name, sub_theme_name, topic_name
    )
    metric_id = metric_manager.get_id_by_name(metric_name)
    geography_type_id = geography_type_manager.get_id_by_name(geography_type)
    geography_id = geography_manager.get_id_by_name(geography_name)

    if any(
        value is None
        for value in (
            theme_id,
            sub_theme_id,
            topic_id,
            metric_id,
            geography_type_id,
            geography_id,
        )
    ):
        return False

    return check_permissions(
        permission_sets=permission_sets.get("permission_sets"),
        theme_id=theme_id,
        sub_theme_id=sub_theme_id,
        topic_id=topic_id,
        metric_id=metric_id,
        geography_type=geography_type_id,
        geography_id=geography_id,
    )


def check_permissions(
    permission_sets: list[PermissionRowType],
    theme_id: int,
    sub_theme_id: int,
    topic_id: int,
    metric_id: int | None = None,
    geography_type: int | None = None,
    geography_id: int | None = None,
) -> bool:
    """
    Core permission evaluation shared by page and chart permission checks.
    """

    if not isinstance(permission_sets, list):
        return False

    for permission_set in permission_sets:
        if geography_type and geography_id:
            if check_metric_related_permissions(
                permission_set=permission_set,
                theme_id=theme_id,
                sub_theme_id=sub_theme_id,
                topic_id=topic_id,
                metric_id=metric_id,
            ) and check_geography_permissions(
                permission_set=permission_set,
                geography_type=geography_type,
                geography_id=geography_id,
            ):
                return True
        elif check_metric_related_permissions(
            permission_set=permission_set,
            theme_id=theme_id,
            sub_theme_id=sub_theme_id,
            topic_id=topic_id,
            metric_id=metric_id,
        ):
            return True

    return False


def check_metric_related_permissions(
    *,
    permission_set: PermissionRowType,
    theme_id: int,
    sub_theme_id: int,
    topic_id: int,
    metric_id: int | None = None,
) -> bool:
    """
    Evaluate the theme/sub-theme/topic/metric portion of a permission row.
    """

    if not isinstance(permission_set, dict):
        return False

    theme_id = str(theme_id)
    sub_theme_id = str(sub_theme_id)
    topic_id = str(topic_id)
    metric_id = str(metric_id)

    permission_theme_id = str(permission_set.get("theme", {}).get("id"))
    permission_sub_theme_id = str(permission_set.get("sub_theme", {}).get("id"))
    permission_topic_id = str(permission_set.get("topic", {}).get("id"))
    permission_metric_id = str(permission_set.get("metric", {}).get("id"))

    if permission_theme_id == WILDCARD_ID_VALUE:
        return True

    if permission_theme_id == theme_id and permission_sub_theme_id == WILDCARD_ID_VALUE:
        return True

    if (
        permission_theme_id == theme_id
        and permission_sub_theme_id == sub_theme_id
        and permission_topic_id in {WILDCARD_ID_VALUE, topic_id}
    ):
        return True

    if (  # noqa: SIM103
        permission_theme_id == theme_id
        and permission_sub_theme_id == sub_theme_id
        and permission_topic_id == topic_id
        and permission_metric_id in {WILDCARD_ID_VALUE, metric_id}
    ):
        return True

    return False


def check_geography_permissions(
    *,
    permission_set: PermissionRowType,
    geography_type: int | None = None,
    geography_id: int | None = None,
) -> bool:
    """
    Evaluate the geography portion of a permission row.
    """

    if not isinstance(permission_set, dict):
        return False

    geography_type = str(geography_type)
    geography_id = str(geography_id)

    permission_geography_type = str(permission_set.get("geography_type", {}).get("id"))
    permission_geography_id = str(permission_set.get("geography", {}).get("id"))

    if permission_geography_type == WILDCARD_ID_VALUE:
        return True

    if (  # noqa: SIM103
        permission_geography_type == geography_type
        and permission_geography_id
        in {
            WILDCARD_ID_VALUE,
            geography_id,
        }
    ):
        return True

    return False
