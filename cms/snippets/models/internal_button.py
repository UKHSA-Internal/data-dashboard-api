from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet


class InternalButtonTypes(models.Choices):
    BULK_DOWNLOAD = "BULK_DOWNLOAD"

    @staticmethod
    def return_button_type_details() -> dict[str, tuple[str, str]]:
        return {
            "BULK_DOWNLOAD": ("/api/bulkdownloads/v1", "POST"),
        }


@register_snippet
class InternalButton(models.Model):
    text = models.CharField(max_length=255)
    button_type = models.CharField(
        max_length=25,
        choices=InternalButtonTypes.choices,
        default=InternalButtonTypes.BULK_DOWNLOAD.value,
        blank=False,
    )
    endpoint = models.CharField(max_length=255, blank=True)
    method = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("text"),
        FieldPanel("button_type"),
    ]

    api_fields = [
        APIField("text"),
        APIField("button_type"),
        APIField("endpoint"),
        APIField("method"),
    ]

    @classmethod
    def get_button_endpoint_details(cls, button_type: str) -> str:
        return InternalButtonTypes.return_button_type_details()[button_type]

    def save(self, *args, **kwargs) -> None:
        """Populates the endpoint and method properties on saved based on button type"""
        endpoint, method = self.get_button_endpoint_details(
            button_type=self.button_type
        )
        self.endpoint = endpoint
        self.method = method
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Text: {self.text} | Type: {self.button_type}"
