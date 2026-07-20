from django import forms
from django.db import models
from wagtail.admin.panels import FieldPanel


class APIApplication(models.Model):
    application_id = models.UUIDField(unique=True)
    application_name = models.CharField(
        max_length=500,
        blank=True,
        editable=True,
        help_text="Application display name",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this application still active?",
    )
    permission_sets = models.ManyToManyField("PermissionSet", blank=True)

    panels = [
        FieldPanel("application_name"),
        FieldPanel("application_id"),
        FieldPanel("is_active"),
        FieldPanel("permission_sets", widget=forms.CheckboxSelectMultiple),
    ]

    def __str__(self):
        return self.application_name or f"API Application {self.id}"
