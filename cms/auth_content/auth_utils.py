import os
from collections.abc import Callable

from django import forms

from cms.dynamic_content import help_texts


def _create_form_field(
    field: dict[str, str | Callable | None],
    wildcard_id_value=None,
    help_text=None,
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
        help_text=help_text or help_texts.NON_PUBLIC_PAGE_REQUIRED,
    )


def _create_required_form_field(
    field: dict[str, str | Callable | None],
    wildcard_id_value=None,
    help_text=None,
) -> forms.CharField:
    form_field = _create_form_field(field, wildcard_id_value, help_text)
    form_field.required = True
    return form_field


def _wildcard_chain_valid(*values):
    """
    Given values ordered from most general to most specific,
    once one is a wildcard (-1), all that follow must be too.
    """
    hit_wildcard = False
    for value in values:
        if hit_wildcard and value != "-1":
            return False
        hit_wildcard = hit_wildcard or value == "-1"
    return True


def is_auth_enabled() -> bool:
    return str(os.environ.get("AUTH_ENABLED", "")).lower() in {"true", "1"}
