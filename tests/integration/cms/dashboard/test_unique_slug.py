import pytest
from django.core.exceptions import ValidationError

from cms.common.models import CommonPage


class TestUKHSAPage:
    @pytest.mark.django_db
    def test_raises_error_if_slug_is_not_unique(self):
        """
        Given multiple existing pages with two parent pages and a single child page
        When the creation of a new page is executed using a matching slug under another parent page
        Then a validation error will be raised.
        """
        # Given
        parent_page_one = CommonPage.objects.create(
            path="abc",
            depth=1,
            title="abc",
            body="abc",
            slug="first-parent-page",
            live=True,
            seo_title="ABC",
        )
        parent_page_two = CommonPage.objects.create(
            path="def",
            depth=1,
            title="def",
            body="def",
            slug="second-parent-page",
            live=True,
            seo_title="ABC",
        )
        child_page_one = CommonPage(
            path="ghi",
            depth=1,
            title="ghi",
            body="ghi",
            slug="first-child-page",
            live=True,
            seo_title="GHI",
        )
        parent_page_one.add_child(instance=child_page_one)

        # When / Then
        with pytest.raises(ValidationError):
            child_page_two = CommonPage(
                path="jkl",
                depth=1,
                title="jkl",
                body="jkl",
                slug="first-child-page",
                live=True,
                seo_title="JKL",
            )
            parent_page_two.add_child(instance=child_page_two)
