import pytest

from cms.forms.managers import EXPECTED_FEEDBACK_PAGE_SLUG
from cms.forms.models import FormPage


class TestFormPageManager:
    @pytest.mark.django_db
    def test_get_feedback_page(self):
        """
        Given 2 `FormPage` records of which only 1 has a slug of "feedback"
        When `get_feedback_page()` is called from the `FormPageManager`
        Then the correct `FormPage` record is returned
        """
        # Given
        feedback_page = FormPage.objects.create(
            path="abc",
            depth=1,
            title="abc",
            slug=EXPECTED_FEEDBACK_PAGE_SLUG,
            seo_title="ABC",
        )
        invalid_page = FormPage.objects.create(
            path="def",
            depth=1,
            title="def",
            slug="invalid_slug",
            seo_title="DEF",
        )

        # When
        retrieved_feedback_page = FormPage.objects.get_feedback_page()

        # Then
        assert retrieved_feedback_page == feedback_page != invalid_page
