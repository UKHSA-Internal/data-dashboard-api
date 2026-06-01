import logging
from typing import Any

from django.apps import apps

WILDCARD_ID_VALUE = "-1"

logger = logging.getLogger(__name__)


def check_permissions_by_name(
    *,
    permission_sets,
    theme_name,
    sub_theme_name,
    topic_name,
    metric_name,
    geography_type,
    geography_name,
) -> bool:
    """
    Convert permission resource names into ids before evaluating chart permissions.
    """

    logger.info("Entered check_permissions_by_name()")

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

    topic_model: Any = apps.get_model("data", "Topic")
    metric_model: Any = apps.get_model("data", "Metric")
    geography_type_model: Any = apps.get_model("data", "GeographyType")
    geography_model: Any = apps.get_model("data", "Geography")

    theme_id, sub_theme_id, topic_id = topic_model.objects.get_id_by_name(
        theme_name, sub_theme_name, topic_name
    )
    metric_id = metric_model.objects.get_id_by_name(metric_name)
    geography_type_id = geography_type_model.objects.get_id_by_name(geography_type)
    geography_id = geography_model.objects.get_id_by_name(geography_name)

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
    permission_sets,
    theme_id,
    sub_theme_id,
    topic_id,
    metric_id=None,
    geography_type=None,
    geography_id=None,
) -> bool:
    """
    Core permission evaluation shared by page and chart permission checks.
    """

    logger.info("Entered check_permissions()")

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
    permission_set,
    theme_id,
    sub_theme_id,
    topic_id,
    metric_id=None,
) -> bool:
    """
    Evaluate the theme/sub-theme/topic/metric portion of a permission row.
    """

    logger.info("Entered check_metric_related_permissions()")

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
    permission_set,
    geography_type=None,
    geography_id=None,
) -> bool:
    """
    Evaluate the geography portion of a permission row.
    """

    logger.info("Entered check_geography_permissions()")

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
