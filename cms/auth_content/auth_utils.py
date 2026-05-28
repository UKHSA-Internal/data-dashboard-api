import logging
from collections.abc import Callable

from cms.auth_content.constants import WILDCARD_ID_VALUE
from django import forms
from cms.dynamic_content import help_texts
from metrics.data.models.core_models.supporting import Geography, GeographyType, Metric, Topic

logger = logging.getLogger(__name__)

def check_permissions(
    permission_sets,
    theme_id,
    sub_theme_id,
    topic_id,
    metric_id=0,
    geography_type=0,
    geography_id=0,
) -> bool:
    if not isinstance(permission_sets, list):
        return False

    # TODO: Can we make them all ID at source?
    theme_id = str(theme_id)
    sub_theme_id = str(sub_theme_id)
    topic_id = str(topic_id)
    metric_id = str(metric_id)
    geography_type = str(geography_type)
    geography_id = str(geography_id)

    for permission in permission_sets:
        permission_theme_id = permission.get("theme", {}).get("id")
        permission_sub_theme_id = permission.get("sub_theme", {}).get("id")
        permission_topic_id = permission.get("topic", {}).get("id")
        permission_metric_id = permission.get("metric", {}).get("id")
        permission_geography_type = permission.get("geography_type", {}).get("id")
        permission_geography_id = permission.get("geography", {}).get("id")
        
        if permission_theme_id == WILDCARD_ID_VALUE:
            return True

        if (
            permission_theme_id == theme_id
            and permission_sub_theme_id == WILDCARD_ID_VALUE
        ):
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

        if (
            permission_theme_id == theme_id
            and permission_sub_theme_id == sub_theme_id
            and permission_topic_id == topic_id
            and permission_metric_id == metric_id
            and permission_geography_type in {WILDCARD_ID_VALUE, geography_type}
        ):
            return True

        if (
            permission_theme_id == theme_id
            and permission_sub_theme_id == sub_theme_id
            and permission_topic_id == topic_id
            and permission_metric_id == metric_id
            and permission_geography_type == geography_type
            and permission_geography_id in {WILDCARD_ID_VALUE, geography_id}
        ):
            return True
        
    return False



def check_permissions_by_name(
    permission_sets,
    theme_name,
    sub_theme_name,
    topic_name,
    metric_name,
    geography_type,
    geography_name,
) -> bool:
    logger.info(f'Entered check_permissions_by_name()')

    theme_id, sub_theme_id, topic_id = Topic.objects.get_id_by_name(theme_name, sub_theme_name, topic_name)
    metric_id = Metric.objects.get_id_by_name(metric_name)
    geography_type_id = GeographyType.objects.get_id_by_name(geography_type)
    geography_id = Geography.objects.get_id_by_name(geography_name)

    # In case a NAME doesn't have an ID
    if any(
            value == -2
            for value in (theme_id, sub_theme_id, topic_id, metric_id, geography_type_id, geography_id)
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
    logger.info(f'Entered check_permission_set()')

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
    else:
        return check_permissions(
            permission_sets.get("permission_sets"),
            theme_id,
            sub_theme_id,
            topic_id,
            metric_id,
            geography_type,
            geography_id,
        )


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
