import pytest

from cms.common.models import CommonPage


class TestCommonPageManager:
    @pytest.mark.django_db
    def test_get_live_pages(self):
        """
        Given 2 `CommonPage` records of which only 1 is live
        When `get_live_pages()` is called from the `CommonPageManager`
        Then the correct `CommonPage` record is returned
        """
        # Given
        live_page = CommonPage.objects.create(
            path="abc",
            depth=1,
            title="abc",
            body="ghi",
            live=True,
            seo_title="ABC",
        )
        unpublished_page = CommonPage.objects.create(
            path="def",
            depth=1,
            title="def",
            body="ghi",
            live=False,
            seo_title="DEF",
        )

        # When
        retrieved_live_pages = CommonPage.objects.get_live_pages()

        # Then
        assert live_page in retrieved_live_pages
        assert unpublished_page not in retrieved_live_pages
