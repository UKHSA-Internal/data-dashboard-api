from collections.abc import Callable

from django import forms


def _create_form_field(field: dict[str, str | Callable | None], wildcard_id_value=None) -> forms.CharField:
    choices = [
        ("", field["field_choice_default"]),
    ]

    if field["field_choice_wildcard"]:
        choices += [(wildcard_id_value, field["field_choice_wildcard"])]

    if field["field_choice_callable"]:
        choices += field["field_choice_callable"]()

    return forms.CharField(
        required=True, label=field["field_label"], widget=forms.Select(choices=choices)
    )

def _initialize_dependent_fields(self):
        """Initialize choices for cascading dependent fields"""
        dependent_fields = {
            "sub_theme": ("Select theme first", "* (All sub-themes)"),
            "topic": ("Select sub-theme first", "* (All topics)"),
            "metric": ("Select topic first", "* (All metrics)"),
            "geography": ("Select geography type first", "* (All geographies)"),
        }

        for field_name, (placeholder, wildcard_label) in dependent_fields.items():
            value = getattr(self.instance, field_name, None)
            if value:
                choices = self._get_field_choices(value, placeholder, wildcard_label)
                self.fields[field_name].widget.choices = choices