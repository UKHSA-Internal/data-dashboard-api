from django import forms

from django.db import models
from django.core.exceptions import ValidationError
from wagtail.admin.panels import FieldPanel

from cms.metrics_interface.field_choices_callables import get_all_geography_type_names_and_ids, get_all_theme_names_and_ids
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

    def clean(self):
        """Validate that this permission set doesn't already exist"""
        cleaned_data = super().clean()

        theme = cleaned_data.get('theme')
        sub_theme = cleaned_data.get('sub_theme')
        topic = cleaned_data.get('topic')
        metric = cleaned_data.get('metric')
        geography_type = cleaned_data.get('geography_type')
        geography = cleaned_data.get('geography')

        # Check if this combination already exists (excluding current instance when editing)
        queryset = PermissionSet.objects.filter(
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            metric=metric,
            geography_type=geography_type,
            geography=geography
        )

        # Exclude current instance when editing
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError(
                "A permission set with this exact combination already exists. "
                "Please modify your selection to create a unique permission set."
            )

        return cleaned_data


class PermissionSet(models.Model):
    name = models.CharField(
        max_length=500,
        blank=True,
        editable=False,  # Don't show in admin form
        help_text="Auto-generated display name"
    )
    theme = models.CharField(
        max_length=255, choices=[("", "---------"), ("-1", "* (All themes)")] + get_all_theme_names_and_ids(), blank=False, default="")
    sub_theme = models.CharField(
        max_length=255, blank=False, default="")
    topic = models.CharField(max_length=255,
                             blank=False, default="")
    metric = models.CharField(
        max_length=255, blank=False, default="")
    geography_type = models.CharField(max_length=255, choices=[(
        "", "---------"), ("-1", "* (All geography-types)")] + get_all_geography_type_names_and_ids(), blank=False, default="")
    geography = models.CharField(
        max_length=255, blank=False, default="")

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
                fields=['theme', 'sub_theme', 'topic',
                        'metric', 'geography_type', 'geography'],
                name='unique_permission_set'
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
        from cms.metrics_interface.field_choices_callables import get_all_theme_names_and_ids

        parts = []

        # Theme
        if self.theme == "-1":
            parts.append("Theme: * (All)")
        elif self.theme:
            theme_name = self._get_choice_label('theme', self.theme)
            parts.append(f"Theme: {theme_name}")

        # Sub-theme (we'll need to store these lookups)
        if self.sub_theme == "-1":
            parts.append("Sub-theme: * (All)")
        elif self.sub_theme:
            sub_theme_name = self._get_choice_label(
                'sub-theme', self.sub_theme)
            parts.append(f"Sub-theme ID: {sub_theme_name}")

        # Topic
        if self.topic == "-1":
            parts.append("Topic: * (All)")
        elif self.topic:
            topic_name = self._get_choice_label(
                'topic', self.topic)
            parts.append(f"Topic: {topic_name}")

        # Metric
        if self.metric == "-1":
            parts.append("Metric: * (All)")
        elif self.metric:
            metric_name = self._get_choice_label(
                'metric', self.metric)
            parts.append(f"Metric: {metric_name}")

        # Geography type (we have the label from enum)
        if self.geography_type == "-1":
            parts.append("Geography Type: * (All)")
        elif self.geography_type:
            geo_type_label = self.geography_type.replace('_', ' ').title()
            parts.append(f"Geography Type: {geo_type_label}")

        # Geography
        if self.geography == "-1":
            parts.append("Geography: * (All)")
        elif self.geography:
            parts.append(f"Geography ID: {self.geography}")

        return " | ".join(parts) if parts else "Permission Set (Not Configured)"

    def _get_choice_label(self, field_name, value):
        """Get the display label for a choice field"""
        if field_name == 'theme':
            from cms.metrics_interface.field_choices_callables import get_all_theme_names_and_ids
            choices = get_all_theme_names_and_ids()
            for choice_value, choice_label in choices:
                if choice_value == value:
                    return choice_label

        if field_name == 'sub-theme':
            from cms.metrics_interface.field_choices_callables import get_all_sub_theme_names_and_ids
            choices = get_all_sub_theme_names_and_ids()
            for choice_value, choice_label in choices:
                if choice_value == value:
                    return choice_label

        if field_name == 'topic':
            from cms.metrics_interface.field_choices_callables import get_all_topic_names_and_ids
            choices = get_all_topic_names_and_ids()
            for choice_value, choice_label in choices:
                if choice_value == value:
                    return choice_label

        if field_name == 'metric':
            from cms.metrics_interface.field_choices_callables import get_all_metric_names_and_ids
            choices = get_all_metric_names_and_ids()
            for choice_value, choice_label in choices:
                if choice_value == value:
                    return choice_label

        return value  # Fallback to ID if not found

    def __str__(self):
        return self.name if self.name else f"Permission Set {self.id}"
