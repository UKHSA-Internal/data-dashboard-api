from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_framework.templatetags.rest_framework import render_markdown
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.api import APIField
from wagtail.models import Page

from cms import seo


class UKHSAPage(Page):
    """Abstract base class for all page types

    Notes:
        Since all page types extend from this class,
        be mindful of changes to fields here.
        As they will incur db migrations
        across multiple page types / tables.

    """

    seo_change_frequency = models.IntegerField(
        verbose_name="SEO change frequency",
        help_text=render_markdown(markdown_text=seo.help_texts.SEO_CHANGE_FREQUENCY),
        default=seo.ChangeFrequency.Monthly,
        choices=seo.ChangeFrequency.choices,
    )
    seo_priority = models.DecimalField(
        verbose_name="SEO priority",
        help_text=seo.help_texts.SEO_PRIORITY,
        default=0.5,
        max_digits=2,
        decimal_places=1,
        validators=[
            MaxValueValidator(Decimal("1.0")),
            MinValueValidator(Decimal("0.1")),
        ],
    )

    api_fields = [
        APIField("seo_change_frequency"),
        APIField("seo_title"),
        APIField("seo_priority"),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel("seo_change_frequency"),
        FieldPanel("seo_priority"),
    ]

    class Meta:
        abstract = True
