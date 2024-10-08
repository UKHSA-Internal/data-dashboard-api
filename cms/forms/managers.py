from django.db import models
from wagtail.models import PageManager
from wagtail.query import PageQuerySet

EXPECTED_FEEDBACK_PAGE_SLUG = "feedback"


class FormPageQuerySet(PageQuerySet):
    """Custom queryset which can be used by the `FormPageManager`"""

    def get_feedback_page(self) -> models.QuerySet:
        """Gets the designated `feedback` page.

        Returns:
            QuerySet: A queryset of the individual feedback page:
                Examples:
                    `<FormPageQuerySet [<FormPage: UKHSA data dashboard feedback>]>`

        """
        return self.filter(slug=EXPECTED_FEEDBACK_PAGE_SLUG)


class FormPageManager(PageManager):
    """Custom model manager class for the `FormPage` model."""

    def get_queryset(self) -> FormPageQuerySet:
        return FormPageQuerySet(model=self.model, using=self.db)

    def get_feedback_page(self) -> "FormPage":
        """Gets the designated `feedback` page.

        Returns:
            The designated form page object
            which has the slug of `feedback`

        """
        return self.get_queryset().get_feedback_page().last()

    def get_feedback_page_form_fields(self):
        feedback_page = self.get_feedback_page()
        try:
            return feedback_page.form_fields.all()
        except AttributeError:
            return []
