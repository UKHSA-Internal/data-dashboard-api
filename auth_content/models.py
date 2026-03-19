from django import forms

from django.db import models
from wagtail.admin.panels import FieldPanel

from cms.metrics_interface.field_choices_callables import get_all_theme_names_and_ids
from validation.enums.geographies_enums import GeographyType
from wagtail.admin.forms import WagtailAdminModelForm


def get_theme_child_map():
    """Returns an object of all parent to child mappings
    e.g.
    {
        infectious_disease: [vaccine_preventable, respiratory ....],
        extreme_event: [weather_alert, mortality_report...]
        ...
    }

    """
    theme_mapping = {}

    print(theme_mapping)
    return theme_mapping


class PermissionSetForm(WagtailAdminModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use CharField with Select widget to bypass choice validation
        self.fields['sub_theme'] = forms.CharField(
            required=False,
            label="Sub Theme",
            widget=forms.Select(choices=[("", "Select theme first")])
        )
        self.fields['topic'] = forms.CharField(
            required=False,
            label="Topic",
            widget=forms.Select(choices=[("", "Select sub-theme first")])
        )
        self.fields['metric'] = forms.CharField(
            required=False,
            label="Metric",
            widget=forms.Select(choices=[("", "Select topic first")])
        )
        self.fields['geography'] = forms.CharField(
            required=False,
            label="Geography",
            widget=forms.Select(
                choices=[("-1", "Select geography type first")])
        )


class PermissionSet(models.Model):
    theme = models.CharField(
        max_length=255, choices=[("", "---------"), ("-1", "* (All themes)")] + get_all_theme_names_and_ids(), blank=True, default="")
    sub_theme = models.CharField(
        max_length=255, blank=True, default="")
    topic = models.CharField(max_length=255,
                             blank=True, default="")
    metric = models.CharField(
        max_length=255, blank=True, default="")
    geography_type = models.CharField(max_length=255, choices=[(
        e.value, e.value.replace("_", " ")) for e in GeographyType], blank=True, default="")
    geography = models.CharField(
        max_length=255, blank=True, default="")

    base_form_class = PermissionSetForm

    panels = [
        FieldPanel("theme"),
        FieldPanel("sub_theme"),
        FieldPanel("topic"),
        FieldPanel("metric"),
        FieldPanel("geography_type"),
        FieldPanel("geography"),
    ]

    def __str__(self):
        if self.theme and self.theme != "" and self.theme != "-1":
            return f"Permission Set - Theme {self.theme}"
        elif self.theme == "-1":
            return "Permission Set - All Themes"
        return "Permission Set - Not Configured"
