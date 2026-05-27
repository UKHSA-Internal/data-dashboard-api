import logging
from collections.abc import Callable
# from cms.auth_content.constants import WILDCARD_ID_VALUE, WILDCARD_NAME_VALUES
from django import forms

from cms.dynamic_content import help_texts

WILDCARD_ID_VALUE = "-1"
WILDCARD_NAME_VALUES = ["* (All themes)", "* (All sub-themes)", "* (All topics)"]

logger = logging.getLogger(__name__)

def check_permissions(user_permissions, theme_id, sub_theme_id, topic_id) -> bool:
    if not isinstance(user_permissions, list):
        return False

    for permission in user_permissions:
        permission_theme_id = permission.get("theme", {}).get("id")
        permission_sub_theme_id = permission.get("sub_theme", {}).get("id")
        permission_topic_id = permission.get("topic", {}).get("id")

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
            and (permission_topic_id in {WILDCARD_ID_VALUE, topic_id})
        ):
            return True

    return False


def check_permissions_by_name(permission_sets, theme_name, sub_theme_name, topic_name) -> bool:
    if not isinstance(permission_sets, dict):
        return False
    if not isinstance(permission_sets.get("permission_sets"), list):
        return False
    if not isinstance(permission_sets.get("summary"), dict):
        return False
    if not isinstance(permission_sets.get("summary").get("has_global_access"), bool):
        return False

    logger.info(f'Entered check_permissions_by_name() with theme "{theme_name}" and sub_theme "{sub_theme_name}" and topic "{topic_name}"')

    if permission_sets.get("summary").get("has_global_access"):
        return True
    else:
        for permission in permission_sets.get("permission_sets"):
            permission_theme_name = permission.get("theme", {}).get("name")
            permission_sub_theme_name = permission.get("sub_theme", {}).get("name")
            permission_topic_name = permission.get("topic", {}).get("name")

            if permission_theme_name in WILDCARD_NAME_VALUES:
                return True

            if (
                permission_theme_name == theme_name
                and permission_sub_theme_name in WILDCARD_NAME_VALUES
            ):
                return True

            if (
                permission_theme_name == theme_name
                and permission_sub_theme_name == sub_theme_name
                and (permission_topic_name in WILDCARD_NAME_VALUES + [topic_name])
            ):
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
