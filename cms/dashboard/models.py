from django.core.validators import MaxValueValidator, MinValueValidator
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.models import Page
from django.db import models

from cms import seo


class UKHSAPage(Page):
    seo_change_frequency = models.IntegerField(
        verbose_name="SEO change frequency",
        help_text=seo.help_texts.SEO_CHANGE_FREQUENCY,
        blank=True,
        null=True,
        choices=seo.ChangeFrequency.choices,
    )
    seo_priority = models.DecimalField(
        verbose_name="SEO priority",
        help_text=seo.help_texts.SEO_PRIORITY,
        null=True,
        blank=True,
        max_digits=3,
        decimal_places=2,
        validators=[
            MaxValueValidator(1.0),
            MinValueValidator(0.099)
        ]
    )

    class Meta:
        abstract = True

    promote_panels = Page.promote_panels + [
        FieldPanel("seo_change_frequency"),
        FieldPanel("seo_priority"),
    ]