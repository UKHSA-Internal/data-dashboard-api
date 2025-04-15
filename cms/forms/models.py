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
from wagtail.models import Orderable

from cms.dashboard.models import AVAILABLE_RICH_TEXT_FEATURES, UKHSAPage
from cms.forms import help_texts
from cms.forms.managers import FormPageManager
from cms.snippets.models.global_banner import BannerTypes


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


class FormPage(AbstractFormUKHSAPage):
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

    announcement_content_panels = [
        InlinePanel("announcements", heading="Announcements", label="Announcement"),
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
            ObjectList(announcement_content_panels, heading="Announcements"),
            ObjectList(confirmation_panels, heading="Confirmation page"),
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
        APIField("announcements"),
    ]

    objects = FormPageManager()


class FormPageAnnouncement(Orderable):
    page = ParentalKey(
        FormPage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
    title = models.CharField(
        max_length=255,
        blank=False,
        help_text=help_texts.ANNOUNCEMENT_BANNER_TITLE,
    )
    badge = models.ForeignKey(
        "whats_new.badge",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = RichTextField(
        max_length=255,
        features=AVAILABLE_RICH_TEXT_FEATURES,
        help_text=help_texts.ANNOUNCEMENT_BANNER_BODY,
    )
    banner_type = models.CharField(
        max_length=50,
        choices=BannerTypes.choices,
        default=BannerTypes.INFORMATION.value,
        help_text=help_texts.ANNOUNCEMENT_BANNER_TYPE,
    )

    is_active = models.BooleanField(
        default=False,
        help_text=help_texts.ANNOUNCEMENT_BANNER_IS_ACTIVE,
    )

    # Sets which panels to show on the editing view
    panels = [
        FieldPanel("title"),
        FieldPanel("badge"),
        FieldPanel("body"),
        FieldPanel("banner_type"),
        FieldPanel("is_active"),
    ]

    # Sets which fields to expose on the API
    api_fields = [
        APIField("title"),
        APIField("badge"),
        APIField("body"),
        APIField("banner_type"),
        APIField("is_active"),
    ]
