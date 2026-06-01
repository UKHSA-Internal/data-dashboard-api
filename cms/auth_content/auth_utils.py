from collections.abc import Callable

from django import forms

from cms.dynamic_content import help_texts


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
