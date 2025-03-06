from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet

from cms.dynamic_content import help_texts
from cms.snippets.managers.global_banner import GlobalBannerManager


class BannerTypes(models.TextChoices):
    INFORMATION = "Information"
    WARNING = "Warning"


AVAILABLE_RICH_TEXT_FEATURES: list[str] = [
    "bold",
    "italic",
    "link",
]


@register_snippet
class GlobalBanner(models.Model):
    title = models.CharField(
        max_length=255,
        blank=False,
        help_text=help_texts.GLOBAL_BANNER_TITLE,
    )
    body = RichTextField(
        max_length=255,
        features=AVAILABLE_RICH_TEXT_FEATURES,
        help_text=help_texts.GLOBAL_BANNER_BODY,
    )
    banner_type = models.CharField(
        max_length=50,
        choices=BannerTypes.choices,
        default=BannerTypes.INFORMATION.value,
        help_text=help_texts.GLOBAL_BANNER_TYPE,
    )
    is_active = models.BooleanField(
        default=False,
        help_text=help_texts.GLOBAL_BANNER_IS_ACTIVE,
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("banner_type"),
        FieldPanel("is_active"),
    ]

    objects = GlobalBannerManager()

    def __str__(self) -> str:
        label = f"Title: {self.title} | Type: {self.banner_type}"
        if self.is_active:
            return f"Active {self.banner_type.lower()}-level global banner"
        return f"Inactive global banner | {label}"
