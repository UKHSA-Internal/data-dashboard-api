from django.db import models
from django.db.models import TextField
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.contrib.forms.models import (
    FORM_FIELD_CHOICES,
    AbstractEmailForm,
    AbstractFormField,
    FormMixin,
)
from wagtail.fields import RichTextField

from cms.dashboard.models import AVAILABLE_RICH_TEXT_FEATURES, UKHSAPage
from cms.dynamic_content.announcements import Announcement
from cms.forms import help_texts
from cms.forms.managers import FormPageManager


class AbstractFormUKHSAPage(FormMixin, UKHSAPage):
    class Meta:
        abstract = True


class FormField(AbstractFormField):
    page = ParentalKey("FormPage", on_delete=models.CASCADE, related_name="form_fields")

    form_field_choices = [
        choice for choice in FORM_FIELD_CHOICES if choice[0] != "multiselect"
    ]

    field_type = models.CharField(
        verbose_name="field type",
        max_length=16,
        choices=form_field_choices,
    )

    def save(self, *args, **kwargs) -> None:
        """
        Since we don't track form submissions in the CMS.
        We override the default behaviour to always update the clean name.
        Regardless of whether the field is new or is being updated in place.
        """
        self.clean_name = self.get_field_clean_name()
        super().save(*args, **kwargs)


class FormPage(AbstractFormUKHSAPage):
    custom_preview_enabled: bool = True

    body = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES, blank=True)

    confirmation_slug = TextField(
        blank=False,
        default="confirmation",
        help_text=help_texts.CONFIRMATION_SLUG_FIELD,
    )
    confirmation_panel_title = TextField(
        blank=True,
        help_text=help_texts.CONFIRMATION_PANEL_TITLE_FIELD,
    )
    confirmation_panel_text = TextField(
        blank=True,
        help_text=help_texts.CONFIRMATION_PANEL_TEXT_FIELD,
    )
    confirmation_body = RichTextField(
        blank=True,
        help_text=help_texts.CONFIRMATION_BODY_FIELD,
    )

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("body"),
        InlinePanel("form_fields", label="Form fields"),
    ]

    confirmation_panels = [
        MultiFieldPanel(
            children=[
                FieldPanel("confirmation_slug"),
                FieldPanel("confirmation_panel_title"),
                FieldPanel("confirmation_panel_text"),
                FieldPanel("confirmation_body"),
            ],
            heading="For the confirmation page",
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(confirmation_panels, heading="Confirmation page"),
            ObjectList(UKHSAPage.announcement_content_panels, heading="Announcements"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    api_fields = UKHSAPage.api_fields + [
        APIField("body"),
        APIField("form_fields"),
        APIField("confirmation_slug"),
        APIField("confirmation_panel_title"),
        APIField("confirmation_panel_text"),
        APIField("confirmation_body"),
    ]

    objects = FormPageManager()


class FormPageAnnouncement(Announcement):
    page = ParentalKey(
        FormPage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
