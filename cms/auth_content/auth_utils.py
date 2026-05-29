import logging
from collections.abc import Callable

from django import forms

from cms.auth_content.constants import WILDCARD_ID_VALUE
from cms.dynamic_content import help_texts
from metrics.data.models.core_models.supporting import (
    Geography,
    GeographyType,
    Metric,
    Topic,
)

logger = logging.getLogger(__name__)


def check_permissions_by_name(
    permission_sets,
    theme_name,
    sub_theme_name,
    topic_name,
    metric_name,
    geography_type,
    geography_name,
) -> bool:
    """
    This is a wrapper that converts permission resource names
    into ids. It is only used to check CHART permissions.
    """

    logger.info("Entered check_permissions_by_name()")

    theme_id, sub_theme_id, topic_id = Topic.objects.get_id_by_name(
        theme_name, sub_theme_name, topic_name
    )
    metric_id = Metric.objects.get_id_by_name(metric_name)
    geography_type_id = GeographyType.objects.get_id_by_name(geography_type)
    geography_id = Geography.objects.get_id_by_name(geography_name)

    # Be safe, just in case a NAME doesn't have an ID
    if any(
        value == -2
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

    return check_permission_set(
        permission_sets,
        theme_id,
        sub_theme_id,
        topic_id,
        metric_id,
        geography_type_id,
        geography_id,
    )


def check_permission_set(
    permission_sets,
    theme_id,
    sub_theme_id,
    topic_id,
    metric_id,
    geography_type,
    geography_id,
) -> bool:
    """
    This is a wrapper that only checks for global permissions, and
    delegates further checks to our core permission checking function.
    It is only used to check CHART permissions.

    @param {dict} permission_sets which contains a permission_sets list, eg:
        {
            "permission_sets": [
                {
                    "theme": {"id": "100", "name": "immunisation"},
                    "sub_theme": {"id": "200", "name": "childhood-vaccines"},
                    "topic": {"id": "-1", "name": "* (All)"},
                    "metric": {"id": "-1", "name": "* (All)"},
                    "geography_type": {"id": "300", "name": "Nation"},
                    "geography": {"id": "-1", "name": "* (All)"},
                }
            ],
            "summary": {"has_global_access": False},
        }
    """

    logger.info("Entered check_permission_set()")

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

    return check_permissions(
        permission_sets.get("permission_sets"),
        theme_id,
        sub_theme_id,
        topic_id,
        metric_id,
        geography_type,
        geography_id,
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
    This is our core permission-checking function It is
    used to check both PAGE & CHART permissions.

    Metric- and geography-related permissions must be
    evaluated separately (spec says).

    @param {list} permission_sets, eg:
        [
              {
                  "theme": {"id": "100", "name": "immunisation"},
                  "sub_theme": {"id": "200", "name": "childhood-vaccines"},
                  "topic": {"id": "-1", "name": "* (All)"},
                  "metric": {"id": "-1", "name": "* (All)"},
                  "geography_type": {"id": "300", "name": "Nation"},
                  "geography": {"id": "-1", "name": "* (All)"},
              }
          ]
    """

    logger.info("Entered check_permissions()")

    if not isinstance(permission_sets, list):
        return False

    for permission_set in permission_sets:
        if geography_type and geography_id:
            # CHART permissions
            if check_metric_related_permissions(
                permission_set, theme_id, sub_theme_id, topic_id, metric_id
            ) and check_geography_permissions(
                permission_set, geography_type, geography_id
            ):
                return True
        else:
            # PAGE permissions
            if check_metric_related_permissions(
                    permission_set, theme_id, sub_theme_id, topic_id, metric_id
            ):
                return True

    return False


def check_metric_related_permissions(
    permission_set,
    theme_id,
    sub_theme_id,
    topic_id,
    metric_id=None,
) -> bool:
    """
    Make sure that every theme, sub_theme, topic and metric
    match or have a wildcard at the end (only look at the
    first 4 attributes of permission_set).

    @param {dict} permission_set, eg:
          {
              "theme": {"id": "100", "name": "immunisation"},
              "sub_theme": {"id": "200", "name": "childhood-vaccines"},
              "topic": {"id": "-1", "name": "* (All)"},
              "metric": {"id": "-1", "name": "* (All)"},
              "geography_type": {"id": "300", "name": "Nation"},
              "geography": {"id": "-1", "name": "* (All)"},
          }
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

    if (
        permission_theme_id == theme_id
        and permission_sub_theme_id == sub_theme_id
        and permission_topic_id == topic_id
        and permission_metric_id in {WILDCARD_ID_VALUE, metric_id}
    ):
        return True

    return False


def check_geography_permissions(
    permission_set,
    geography_type=None,
    geography_id=None,
) -> bool:
    """
    Make sure that both geography_type and geography
    match or have a wildcard at the end (only look at the
    first 2 attributes of permission_set).

    @param {dict} permission_set, eg:
          {
              "theme": {"id": "100", "name": "immunisation"},
              "sub_theme": {"id": "200", "name": "childhood-vaccines"},
              "topic": {"id": "-1", "name": "* (All)"},
              "metric": {"id": "-1", "name": "* (All)"},
              "geography_type": {"id": "300", "name": "Nation"},
              "geography": {"id": "-1", "name": "* (All)"},
          }
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

    if permission_geography_type == geography_type and permission_geography_id in {
        WILDCARD_ID_VALUE,
        geography_id,
    }:
        return True

    return False


def _create_form_field(
    field: dict[str, str | Callable | None], wildcard_id_value=None
) -> forms.CharField:
    choices = [
        ("", field["field_choice_default"]),
    ]

    if field["field_choice_wildcard"]:
        choices += [(wildcard_id_value, field["field_choice_wildcard"])]

    if field["field_choice_callable"]:
        choices += field["field_choice_callable"]()

    return forms.CharField(
        required=False,
        label=field["field_label"],
        widget=forms.Select(choices=choices),
        help_text=help_texts.NON_PUBLIC_PAGE_REQUIRED,
    )
