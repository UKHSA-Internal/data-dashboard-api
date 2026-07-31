from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField

from cms.dynamic_content import help_texts


class DataClassificationLevels(models.TextChoices):
    """
    Choices available for a page's classification.
    """

    OFFICIAL = "official"
    OFFICIAL_SENSITIVE = "official_sensitive"
    PROTECTIVE_MARKING_NOT_SET = "protective_marking_not_set"
    SECRET = "secret"  # nosec #noqa: S105
    TOP_SECRET = "top_secret"  # nosec #noqa: S105


class NonPublicPage(models.Model):
    """
    An abstract model to be reused on pages which require non-public access control.
    """

    class Meta:
        abstract = True

    # whether the page should be publicly available or not
    is_public = models.BooleanField(
        # default to non-public for safety so that DPD have to actively choose for a page to be public
        default=False,
        verbose_name="enable public page",
    )

    # each non-public page has a classification, public pages will end up with an empty string value
    page_classification = models.CharField(
        max_length=50,
        choices=DataClassificationLevels.choices,
        # default to empty string to indicate no classification for pages that aren't non-public
        default="",
        help_text=help_texts.PAGE_CLASSIFICATION,
        blank=True,
    )

    # these are attributes which are used to determine user access to the page. They map directly to the permission sets
    # theme, sub_theme, and topic. Metric and geographic based access aren't implemented yet.
    page_theme = models.CharField(max_length=255, blank=True, default="")
    page_sub_theme = models.CharField(max_length=255, blank=True, default="")
    page_topic = models.CharField(max_length=255, blank=True, default="")

    # provide a default content panel list for subclasses to use if they want
    content_panels = [
        # always show the enable public page checkbox
        FieldPanel("is_public"),
        # then group the non-public page specific options into a panel of their own which is collapsed by default
        MultiFieldPanel(
            heading="Non-public page options",
            classname="collapsed",
            children=[
                FieldPanel("page_classification"),
                FieldPanel("page_theme"),
                FieldPanel("page_sub_theme"),
                FieldPanel("page_topic"),
            ],
        ),
    ]

    # provide a default set of fields which should be exposed through the api in subclasses
    api_fields = [
        APIField("is_public"),
        APIField("page_classification"),
    ]

    def clean(self):
        super().clean()
        if self.is_public:
            self._reset_for_public_page()
        else:
            self._validate_non_public_page()

    def _reset_for_public_page(self):
        """
        Return this page's specific non-public attributes back to their defaults.
        """
        # all of these are only relevant for non-public pages, hence, empty strings
        self.page_classification = ""
        self.page_theme = ""
        self.page_sub_theme = ""
        self.page_topic = ""

    def _validate_non_public_page(self):
        """
        Validates the selected values on this page for the non-public attributes.
        """
        if not self.page_classification:
            raise ValidationError(
                {
                    "page_classification": "Please select a classification level for this non-public page"
                }
            )
        if not self.page_theme:
            raise ValidationError(
                {"page_theme": "Please select a theme for this non-public page"}
            )
        if not self.page_sub_theme:
            raise ValidationError(
                {"page_sub_theme": "Please select a sub theme for this non-public page"}
            )
        if not self.page_topic:
            raise ValidationError(
                {"page_topic": "Please select a topic for this non-public page"}
            )
