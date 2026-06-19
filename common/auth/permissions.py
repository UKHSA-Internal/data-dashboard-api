import logging
from typing import TypedDict

from ingestion.metrics_interface.interface import MetricsAPIInterface

logger = logging.getLogger(__name__)

WILDCARD_ID_VALUE = "-1"

"""
    A few classes with type hints to represent our complete
    JWT permission set hierarchy. Please do import and use
    this from other modules too to keep us safe & well:
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


def check_chart_permissions_by_name(
    *,
    permission_sets: PermissionSetsType,
    theme_name: str,
    sub_theme_name: str,
    topic_name: str,
    metric_name: str,
    geography_type: str,
    geography_name: str,
) -> bool:
    """Convert permission resource names into ids (before checking CHART permissions)."""

    if not isinstance(permission_sets, dict):
        logger.info("check_chart_permissions_by_name: permission_sets is not a dict")
        return False
    if not isinstance(permission_sets.get("permission_sets"), list):
        logger.info("check_chart_permissions_by_name: permission_sets not a list")
        return False
    if not isinstance(permission_sets.get("summary"), dict):
        logger.info("check_chart_permissions_by_name: summary a dict")
        return False
    if not isinstance(permission_sets.get("summary").get("has_global_access"), bool):
        logger.info("check_chart_permissions_by_name: has_global_access not a bool")
        return False

    if permission_sets.get("summary").get("has_global_access"):
        logger.info(
            "check_chart_permissions_by_name: has_global_access=True, therefore granting access"
        )
        return True

    topic_manager = MetricsAPIInterface.get_topic_manager()
    metric_manager = MetricsAPIInterface.get_metric_manager()
    geography_type_manager = MetricsAPIInterface.get_geography_type_manager()
    geography_manager = MetricsAPIInterface.get_geography_manager()

    theme_id, sub_theme_id, topic_id = topic_manager.get_id_by_name(
        theme_name, sub_theme_name, topic_name
    )
    metric_id = metric_manager.get_id_by_name(metric_name)
    geography_type_id = geography_type_manager.get_id_by_name(geography_type)
    geography_id = geography_manager.get_code_by_name(geography_name, geography_type)

    logger.info(
        "check_chart_permissions_by_name: The resolved IDs are: theme=%s sub_theme=%s topic=%s metric=%s geography_type=%s geography=%s",
        theme_id,
        sub_theme_id,
        topic_id,
        metric_id,
        geography_type_id,
        geography_id,
    )

    # Sanity check, because front-end must always
    # send content for any of these 6 requests
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
        logger.info(
            "check_chart_permissions_by_name: Some resource IDs could not be resolved, therefore denying access"
        )
        return False

    result = check_chart_permissions(
        permission_sets=permission_sets.get("permission_sets"),
        theme_id=theme_id,
        sub_theme_id=sub_theme_id,
        topic_id=topic_id,
        metric_id=metric_id,
        geography_type=geography_type_id,
        geography_id=geography_id,
    )

    logger.info("check_chart_permissions_by_name: final result=%s", result)

    return result


def check_chart_permissions(  # noqa: PLR0914
    *,
    permission_sets: list[PermissionRowType],
    theme_id: str,
    sub_theme_id: str,
    topic_id: str,
    metric_id: str,
    geography_type: str,
    geography_id: str,
) -> bool:
    """Check permissions whether the end-user can access a specific CHART through the API."""

    if not isinstance(permission_sets, list):
        return False

    resource_ids = _normalize_resource_ids(
        theme_id,
        sub_theme_id,
        topic_id,
        metric_id,
        geography_type,
        geography_id,
    )
    if resource_ids is None:
        return False
    (
        theme_id,
        sub_theme_id,
        topic_id,
        metric_id,
        geography_type,
        geography_id,
    ) = resource_ids

    for permission_set in permission_sets:
        if not isinstance(permission_set, dict):
            return False

        permission_ids = _normalize_permission_ids(
            "theme",
            "sub_theme",
            "topic",
            "metric",
            "geography_type",
            "geography",
            permission_set=permission_set,
        )

        # All permission fields must be present
        if permission_ids is None:
            logger.info(
                "check_chart_permissions: The permission_set has missing fields, therefore denying access"
            )
            return False
        (
            permission_theme_id,
            permission_sub_theme_id,
            permission_topic_id,
            permission_metric_id,
            permission_geography_type,
            permission_geography_id,
        ) = permission_ids

        # Themes, sub themes, topics & metrics have their own
        # dependency hierarchy (means wildcards can be at the end)
        has_theme_sub_theme_topic_permissions = check_theme_sub_theme_topic_permissions(
            permission_theme_id=permission_theme_id,
            permission_sub_theme_id=permission_sub_theme_id,
            permission_topic_id=permission_topic_id,
            theme_id=theme_id,
            sub_theme_id=sub_theme_id,
            topic_id=topic_id,
        )
        has_metric_permissions = check_metric_permissions(
            permission_metric_id=permission_metric_id,
            metric_id=metric_id,
        )

        # Geographies have their own dependency hierarchy too
        has_geography_permissions = check_geography_permissions(
            permission_geography_type=permission_geography_type,
            permission_geography_id=permission_geography_id,
            geography_type=geography_type,
            geography_id=geography_id,
        )

        logger.info(
            "check_chart_permissions: The permission_set(theme=%s sub=%s topic=%s metric=%s geo_type=%s geo=%s) with "
            "request(theme=%s sub=%s topic=%s metric=%s geo_type=%s geo=%s) resulted in: "
            "→ has_theme_sub_theme_topic_permissions=%s has_metric_permissions=%s has_geography_permissions=%s",
            permission_theme_id,
            permission_sub_theme_id,
            permission_topic_id,
            permission_metric_id,
            permission_geography_type,
            permission_geography_id,
            theme_id,
            sub_theme_id,
            topic_id,
            metric_id,
            geography_type,
            geography_id,
            has_theme_sub_theme_topic_permissions,
            has_metric_permissions,
            has_geography_permissions,
        )

        if (
            has_theme_sub_theme_topic_permissions
            and has_metric_permissions
            and has_geography_permissions
        ):
            return True

    return False


def check_page_permissions(
    *,
    permission_sets: list[PermissionRowType],
    theme_id: str,
    sub_theme_id: str,
    topic_id: str,
) -> bool:
    """Check permissions whether the end-user can access a specific CMS PAGE through the API."""

    if not isinstance(permission_sets, list):
        return False

    resource_ids = _normalize_resource_ids(theme_id, sub_theme_id, topic_id)
    if resource_ids is None:
        return False
    theme_id, sub_theme_id, topic_id = resource_ids

    for permission_set in permission_sets:
        if not isinstance(permission_set, dict):
            return False

        # Theme must be present, but other permission fields are
        # optional, as wildcard hierarchy allows early short-circuit
        permission_theme_id = _normalize_permission_id(
            field_name="theme", permission_set=permission_set
        )
        if permission_theme_id is None:
            return False
        permission_sub_theme_id = (
            _normalize_permission_id(
                field_name="sub_theme", permission_set=permission_set
            )
            or ""
        )
        permission_topic_id = (
            _normalize_permission_id(field_name="topic", permission_set=permission_set)
            or ""
        )

        if check_theme_sub_theme_topic_permissions(
            permission_theme_id=permission_theme_id,
            permission_sub_theme_id=permission_sub_theme_id,
            permission_topic_id=permission_topic_id,
            theme_id=theme_id,
            sub_theme_id=sub_theme_id,
            topic_id=topic_id,
        ):
            return True

    return False


def check_theme_sub_theme_topic_permissions(
    *,
    permission_theme_id: str,
    permission_sub_theme_id: str,
    permission_topic_id: str,
    theme_id: str,
    sub_theme_id: str,
    topic_id: str,
) -> bool:
    """
    Evaluate the theme/sub-theme/topic portion of a permission row
    with its own dependency hierarchy (means wildcards can be at the end)
    """

    if permission_theme_id == WILDCARD_ID_VALUE:
        return True

    if permission_theme_id == theme_id and permission_sub_theme_id == WILDCARD_ID_VALUE:
        return True

    if (  # noqa: SIM103
        permission_theme_id == theme_id
        and permission_sub_theme_id == sub_theme_id
        and (permission_topic_id in {WILDCARD_ID_VALUE, topic_id})
    ):
        return True

    return False


def check_metric_permissions(
    *,
    permission_metric_id: str,
    metric_id: str,
) -> bool:
    """
    Evaluate the metric portion of a permission row
    for it to be either a wildcard or a match.
    """

    if permission_metric_id in {WILDCARD_ID_VALUE, metric_id}:  # noqa: SIM103
        return True

    return False


def check_geography_permissions(
    *,
    permission_geography_type: str,
    permission_geography_id: str,
    geography_type: str,
    geography_id: str,
) -> bool:
    """
    Evaluate the geography_type/geography portion of a permission row
    with its own dependency hierarchy (means wildcards can be at the end)
    """

    if permission_geography_type == WILDCARD_ID_VALUE:
        return True

    if (  # noqa: SIM103
        permission_geography_type == geography_type
        and permission_geography_id in {WILDCARD_ID_VALUE, geography_id}
    ):
        return True

    return False


def _get_id_string_or_none(my_id: int | str | None) -> str | None:
    """Normalize id to string whilst preserving None values"""

    return str(my_id) if my_id is not None else None


def _normalize_resource_ids(*ids: int | str | None) -> tuple[str, ...] | None:
    """Normalize all resource ids and return them as tuple of strings."""

    normalized_ids = tuple(_get_id_string_or_none(my_id) for my_id in ids)

    if _has_missing_ids(*normalized_ids):
        return None

    return normalized_ids


def _normalize_permission_ids(
    *field_names: str,
    permission_set: PermissionRowType | dict,
) -> tuple[str, ...] | None:
    """Extract and normalize permission ids as tuple of strings."""

    normalized_ids = tuple(
        _normalize_permission_id(field_name=field_name, permission_set=permission_set)
        for field_name in field_names
    )

    if _has_missing_ids(*normalized_ids):
        return None

    return normalized_ids


def _normalize_permission_id(
    *, field_name: str, permission_set: PermissionRowType | dict
) -> str | None:
    """Extract and normalize the permission id from a permission row."""

    return _get_id_string_or_none(permission_set.get(field_name, {}).get("id"))


def _has_missing_ids(*ids: str | None) -> bool:
    """Check if any required id is missing, and if so normalize it to be None."""

    return any(my_id is None for my_id in ids)
