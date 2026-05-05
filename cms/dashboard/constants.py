from cms.metrics_interface.field_choices_callables import (
    get_all_theme_names_and_ids,
    get_all_metric_names_and_ids,
)

THEME_FIELDS = [
    {
        "field_name": "theme",
        "field_label": "Theme",
        "field_choice_default": "----------",
        "field_choice_wildcard": None,
        "field_choice_callable": get_all_theme_names_and_ids,
    },
    {
        "field_name": "sub_theme",
        "field_label": "Sub Theme",
        "field_choice_default": "Select theme first",
        "field_choice_wildcard": None,
        "field_choice_callable": None,
    },
    {
        "field_name": "topic",
        "field_label": "Topic",
        "field_choice_default": "Select sub-theme first",
        "field_choice_wildcard": None,
        "field_choice_callable": None,
    },
    {
        "field_name": "metric",
        "field_label": "Metric",
        "field_choice_default": "Select topic first",
        "field_choice_wildcard": None,
        "field_choice_callable": get_all_metric_names_and_ids,
    },
]

