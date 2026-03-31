from itertools import starmap
from typing import Callable

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.admin.panels import FieldPanel

from auth_content.constants import PERMISSION_SET_FIELDS
from cms.metrics_interface.field_choices_callables import (
    get_all_geography_type_names_and_ids,
    get_all_metric_names_and_ids,
    get_all_sub_theme_names_and_ids,
    get_all_theme_names_and_ids,
    get_all_topic_names_and_ids,
)


def get_theme_child_map():
    """Returns an object of all parent to child mappings
    e.g.
    {
        infectious_disease: [vaccine_preventable, respiratory ....],
        extreme_event: [weather_alert, mortality_report...]
        ...
    }

    """
    return {}


def _create_form_field(field: dict[str, str | Callable | None]) -> forms.CharField:
    choices = [("", field["field_choice_default"]),]

    if field["field_choice_wildcard"]:
        choices += [("-1", field["field_choice_wildcard"])]

    if field["field_choice_callable"]:
        choices += field["field_choice_callable"]()

    return forms.CharField(
        required=True,
        label=field["field_label"],
        widget=forms.Select(choices=choices)
    )


class PermissionSetForm(WagtailAdminModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use CharField with Select widget to bypass choice validation
        for field in PERMISSION_SET_FIELDS:
            self.fields[field["field_name"]] = _create_form_field(field)

        if self.instance and self.instance.pk:
            # Sub-theme
            if self.instance.sub_theme and self.instance.sub_theme != "-1":
                self.fields["sub_theme"].widget.choices = [
                    ("", "Select theme first"),
                    (
                        self.instance.sub_theme,
                        f"Loading... (ID: {self.instance.sub_theme})",
                    ),
                ]
            elif self.instance.sub_theme == "-1":
                self.fields["sub_theme"].widget.choices = [
                    ("-1", "* (All sub-themes)")]

            # Topic
            if self.instance.topic and self.instance.topic != "-1":
                self.fields["topic"].widget.choices = [
                    ("", "Select sub-theme first"),
                    (self.instance.topic,
                     f"Loading... (ID: {self.instance.topic})"),
                ]
            elif self.instance.topic == "-1":
                self.fields["topic"].widget.choices = [
                    ("-1", "* (All topics)")]

            # Metric
            if self.instance.metric and self.instance.metric != "-1":
                self.fields["metric"].widget.choices = [
                    ("", "Select topic first"),
                    (self.instance.metric,
                     f"Loading... (ID: {self.instance.metric})"),
                ]
            elif self.instance.metric == "-1":
                self.fields["metric"].widget.choices = [
                    ("-1", "* (All metrics)")]

            # Geography
            if self.instance.geography and self.instance.geography != "-1":
                self.fields["geography"].widget.choices = [
                    ("", "Select geography type first"),
                    (
                        self.instance.geography,
                        f"Loading... (ID: {self.instance.geography})",
                    ),
                ]
            elif self.instance.geography == "-1":
                self.fields["geography"].widget.choices = [
                    ("-1", "* (All geographies)")
                ]

    def clean(self):
        """Validate that this permission set doesn't already exist"""
        cleaned_data = super().clean()

        theme = cleaned_data.get("theme")
        sub_theme = cleaned_data.get("sub_theme")
        topic = cleaned_data.get("topic")
        metric = cleaned_data.get("metric")
        geography_type = cleaned_data.get("geography_type")
        geography = cleaned_data.get("geography")

        # Check if this combination already exists (excluding current instance when editing)
        queryset = PermissionSet.objects.filter(
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            metric=metric,
            geography_type=geography_type,
            geography=geography,
        )

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError(
                message="A permission set with this exact combination already exists. Please modify your selection to create a unique permission set."
            )

        return cleaned_data


class PermissionSet(models.Model):
    name = models.CharField(
        max_length=500,
        blank=True,
        editable=False,
        help_text="Auto-generated display name",
    )
    theme = models.CharField(max_length=255, blank=False, default="")
    sub_theme = models.CharField(max_length=255, blank=False, default="")
    topic = models.CharField(max_length=255, blank=False, default="")
    metric = models.CharField(max_length=255, blank=False, default="")
    geography_type = models.CharField(max_length=255, blank=False, default="")
    geography = models.CharField(max_length=255, blank=False, default="")

    base_form_class = PermissionSetForm

    panels = [
        FieldPanel("theme"),
        FieldPanel("sub_theme"),
        FieldPanel("topic"),
        FieldPanel("metric"),
        FieldPanel("geography_type"),
        FieldPanel("geography"),
    ]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "theme",
                    "sub_theme",
                    "topic",
                    "metric",
                    "geography_type",
                    "geography",
                ],
                name="unique_permission_set",
            )
        ]

    def save(self, *args, **kwargs):
        """Generate the display name before saving"""
        self.name = self._generate_display_name()
        super().save(*args, **kwargs)

    def _generate_display_name(self):
        """
        Generate display name using the selected dropdown labels.
        This uses the form's choice labels, not database lookups.
        """

        def format_field(field_name: str, field_value: str, label: str) -> str | None:
            """
            Format a single field for display.

            Args:
                field_name: The field identifier (e.g., "theme", "sub-theme")
                field_value: The stored value (ID or "-1")
                label: The display label (e.g., "Theme", "Sub-theme")

            Returns:
                Formatted string or None if field is empty
            """
            if not field_value:
                return None

            if field_value == "-1":
                return f"{label}: * (All)"

            # Special case for geography_type - format the enum value
            if field_name == "geography_type":
                formatted_value = field_value.replace("_", " ").title()
                return f"{label}: {formatted_value}"

            # For other fields, use choice label lookup
            choice_label = self._get_choice_label(field_name, field_value)
            return f"{label}: {choice_label}"

        fields = [
            ("theme", self.theme, "Theme"),
            ("sub-theme", self.sub_theme, "Sub-theme"),
            ("topic", self.topic, "Topic"),
            ("metric", self.metric, "Metric"),
            ("geography_type", self.geography_type, "Geography Type"),
            ("geography", self.geography, "Geography"),
        ]

        parts = [p for p in starmap(format_field, fields) if p is not None]

        return " | ".join(parts) if parts else "Permission Set (Not Configured)"

    def _get_choice_label(self, field_name: str, value: str) -> str:
        """Get the display label for a choice field"""

        field_lookup_map = {
            "theme": get_all_theme_names_and_ids,
            "sub-theme": get_all_sub_theme_names_and_ids,
            "topic": get_all_topic_names_and_ids,
            "metric": get_all_metric_names_and_ids,
        }

        # Get the appropriate lookup function
        lookup_func = field_lookup_map.get(field_name)

        if lookup_func:
            choices = lookup_func()
            return self._find_label_in_choices(choices, value)

        return value

    @staticmethod
    def _find_label_in_choices(choices: list[tuple], value: str) -> str:
        """
        Find the label for a given value in a list of (value, label) tuples.

        Args:
            choices: List of (value, label) tuples
            value: The value to look up

        Returns:
            The label if found, otherwise the original value
        """
        return next(
            (label for choice_value, label in choices if choice_value == value),
            value,  # default if not found
        )

    def __str__(self):
        return self.name or f"Permission Set {self.id}"
