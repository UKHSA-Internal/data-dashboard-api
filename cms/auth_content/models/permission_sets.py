from itertools import starmap

from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.panels import FieldPanel, mark_safe

from cms.auth_content.auth_utils import _create_form_field
from cms.auth_content.constants import PERMISSION_SET_FIELDS
from cms.dynamic_content import help_texts
from cms.metrics_interface.field_choices_callables import (
    get_all_geography_names_and_codes,
    get_all_geography_type_names_and_ids,
    get_all_metric_names_and_ids,
    get_all_sub_theme_names_and_ids,
    get_all_theme_names_and_ids,
    get_all_topic_names_and_ids,
)
from common.auth.permissions import WILDCARD_ID_VALUE

# TODO: For the 6th AC - is this just a validity check that we can add into to_predicate? There are other places we check permissions...
#       and they don't use the function, so would have to move that validity check out somewhere else too...
class PermissionSetForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in PERMISSION_SET_FIELDS:
            self.fields[field["field_name"]] = _create_form_field(
                field, WILDCARD_ID_VALUE, True, help_texts.FIELD_REQUIRED
            )

        if (self.instance and self.instance.pk) or getattr(self, "is_bound", False):
            self._initialize_dependent_fields()

    def _initialize_dependent_fields(self):
        """Initialize choices for cascading dependent fields"""
        dependent_fields = {
            "sub_theme": ("Select theme first", "* (All sub-themes)"),
            "topic": ("Select sub-theme first", "* (All topics)"),
            "metric": ("Select topic first", "* (All metrics)"),
            "geography": ("Select geography type first", "* (All geographies)"),
        }

        for field_name, (placeholder, wildcard_label) in dependent_fields.items():
            value = self._get_dependent_field_value(field_name)
            if value:
                choices = self._get_field_choices(value, placeholder, wildcard_label)
                self.fields[field_name].widget.choices = choices

    def _get_dependent_field_value(self, field_name: str):
        if getattr(self, "is_bound", False):
            return self.data.get(field_name)

        return getattr(self.instance, field_name, None)

    @staticmethod
    def _get_field_choices(value, placeholder, wildcard_label):
        """Generate choices list based on field value"""
        if value == WILDCARD_ID_VALUE:
            return [(WILDCARD_ID_VALUE, wildcard_label)]
        return [("", placeholder), (value, f"Loading... (ID: {value})")]

    # def clean(self):
    #     """Validate that this permission set doesn't already exist"""
    #     cleaned_data = super().clean()

    #     theme = cleaned_data.get("theme")
    #     sub_theme = cleaned_data.get("sub_theme")
    #     topic = cleaned_data.get("topic")
    #     metric = cleaned_data.get("metric")
    #     geography_type = cleaned_data.get("geography_type")
    #     geography = cleaned_data.get("geography")

        # Add errors like this, can do both sections and name separate
        # so all errors can be displayed at once
        # self.add_error()

        # TODO: There's a thing about migrating/fixing existing invalid permissions sets
        #       I think that should only be handling the empty values and treating those as no access?

        # Some of the stuff on the ticket - I think just comes down to
        # lower permissions being overridden by having all higher
        # e.g. if you have all themes, one specific metric
        # that equates to just having everything

        # TODO: With them marked as required I don't think this check is needed? Might even be able to remove this function entirely
        # if not theme:
        #     raise ValidationError("Missing theme")
        # elif not sub_theme:
        #     raise ValidationError({"sub_theme": "Please select a sub_theme for this permission set"})
        # elif not topic:
        #     raise ValidationError("Missing topic")
        # elif not metric:
        #     raise ValidationError("Missing metric")
        # elif not geography_type:
        #     raise ValidationError("Missing geography type")
        # elif not geography:
        #     raise ValidationError("Missing geography")

        # return cleaned_data

    class Media:
        js = ["js/permission_set.js"]


class PermissionSet(models.Model):
    name = models.CharField(
        max_length=500,
        blank=True,
        editable=False,
        help_text="Auto-generated display name",
    )
    display_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=help_texts.PERMISSION_SET_DISPLAY_NAME,
    )
    theme = models.CharField(max_length=255, blank=False, default="")
    sub_theme = models.CharField(max_length=255, blank=False, default="")
    topic = models.CharField(max_length=255, blank=False, default="")
    metric = models.CharField(max_length=255, blank=False, default="")
    geography_type = models.CharField(max_length=255, blank=False, default="")
    geography = models.CharField(max_length=255, blank=False, default="")

    base_form_class = PermissionSetForm

    @property
    def permission_set_details(self):
        parts = [part.strip() for part in self.name.split("|")]
        return mark_safe("<br>".join(parts))

    panels = [
        FieldPanel("display_name"),
        FieldPanel("theme"),
        FieldPanel("sub_theme"),
        FieldPanel("topic"),
        FieldPanel("metric"),
        FieldPanel("geography_type"),
        FieldPanel("geography"),
    ]

    def field_combination_valid(self):
        return not ((self.theme == "-1" and (self.sub_theme != "-1" or self.topic != "-1" or self.metric != "-1")) \
                    or (self.sub_theme == "-1" and (self.topic != "-1" or self.metric != "-1")) \
                    or (self.topic == "-1" and self.metric != "-1") \
                    or (self.geography_type == "-1" and self.geography != "-1"))

    def clean(self):
        if not self.field_combination_valid():
                # TODO: Proper error message
                raise ValidationError("Invalid permission set - model clean")
        return super().clean()

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
                violation_error_message="A permission set with this exact combination already exists. Please modify your selection to create a unique permission set."
            ),
            models.UniqueConstraint(
                fields=["display_name"],
                condition=models.Q(display_name__isnull=False),
                name="unique_non_null_display_name",
            ),
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
                field_value: The stored value (ID or WILDCARD_ID_VALUE)
                label: The display label (e.g., "Theme", "Sub-theme")

            Returns:
                Formatted string or None if field is empty
            """
            if not field_value:
                return None

            if field_value == WILDCARD_ID_VALUE:
                return f"{label}: * (All)"

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
            "geography_type": get_all_geography_type_names_and_ids,
            "geography": get_all_geography_names_and_codes,
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
        return self.display_name or self.name or f"Permission Set {self.id}"
