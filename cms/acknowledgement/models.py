from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.search import index

from cms.acknowledgement.managers import AcknowledgementPageManager
from cms.dashboard.models import (
    MAXIMUM_URL_FIELD_LENGTH,
    UKHSAPage,
)


class AcknowledgementPage(
    UKHSAPage
):  # inherit from our UKHSAPage instead of Wagtail's Page
    body = RichTextField(features=[], blank=True)
    i_agree_checkbox = models.CharField(max_length=255)
    terms_of_service_link_text = models.CharField(max_length=50)
    terms_of_service_link = models.URLField(
        max_length=MAXIMUM_URL_FIELD_LENGTH, verbose_name="Terms of service link"
    )
    disagree_button = models.CharField(max_length=50)
    agree_button = models.CharField(max_length=50)

    search_fields = UKHSAPage.search_fields + [
        index.SearchField("body"),
    ]

    content_panels = UKHSAPage.content_panels + [
        FieldPanel("body"),
        FieldPanel("terms_of_service_link_text"),
        FieldPanel("terms_of_service_link"),
        FieldPanel("i_agree_checkbox"),
        FieldPanel("disagree_button"),
        FieldPanel("agree_button"),
    ]

    # Expose via Wagtail API
    api_fields = [
        APIField("title"),
        APIField("body"),
        APIField("terms_of_service_link_text"),
        APIField("terms_of_service_link"),
        APIField("i_agree_checkbox"),
        APIField("disagree_button"),
        APIField("agree_button"),
    ]

    objects = AcknowledgementPageManager()

    @classmethod
    def is_previewable(cls) -> bool:
        """Returns False. Since this is a headless CMS the preview panel is not supported"""
        return False
